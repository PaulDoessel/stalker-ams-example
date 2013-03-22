# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of Stalker and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import datetime
import unittest

from sqlalchemy import Column, Integer, ForeignKey
from stalker.conf import defaults
from stalker.models.mixins import ScheduleMixin
from stalker.db.session import DBSession
from stalker.models.entity import SimpleEntity


class SchedMixFooMixedInClass(SimpleEntity, ScheduleMixin):
    """a class which derives from another which has and __init__ already
    """

    __tablename__ = "SchedMixFooMixedInClasses"
    __mapper_args__ = {"polymorphic_identity": "SchedMixFooMixedInClass"}
    schedMixFooMixedInClass_id = Column("id", Integer,
                                        ForeignKey("SimpleEntities.id"),
                                        primary_key=True)

    def __init__(self, **kwargs):
        super(SchedMixFooMixedInClass, self).__init__(**kwargs)
        ScheduleMixin.__init__(self, **kwargs)

class ScheduleMixinTester(unittest.TestCase):
    """Tests the ScheduleMixin
    """
    
    def setUp(self):
        """setup the test
        """
        # create mock objects
        self.start = datetime.datetime(2013, 3, 22, 15, 15)
        self.end = self.start + datetime.timedelta(days=20)
        self.duration = datetime.timedelta(days=10)

        self.kwargs = {
            'name': 'Test Schedule Mixin',
            'description': 'This is a simple entity object for testing '
                           'ScheduleMixin',
            'start': self.start,
            'end': self.end,
            'duration': self.duration,
            'resolution': datetime.timedelta(minutes=30)
        }

        self.mock_foo_obj = SchedMixFooMixedInClass(**self.kwargs)
    
    def tearDown(self):
        """clean up the test
        """
        DBSession.remove()
    
    def test_start_argument_is_not_a_date_object(self):
        """testing if defaults will be used for the start attribute when
        the start is given as something other than a datetime.datetime object
        """
        test_values = [1, 1.2, "str", ["a", "date"]]
        
        for test_value in test_values:
            self.kwargs["start"] = test_value

            new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)

            self.assertEqual(new_foo_obj.start,
                             new_foo_obj.end - new_foo_obj.duration)
            
            # the values are rounded can not check anymore
            #self.assertEqual(new_foo_obj.end, self.kwargs["end"])
            #self.assertEqual(new_foo_obj.duration, self.kwargs["duration"])
    
    def test_start_attribute_is_not_a_date_object(self):
        """testing if the defaults will be used when trying to set the
        start attribute to something other than a datetime.datetime object
        """
        test_values = [1, 1.2, "str", ["a", "date"]]
        
        for test_value in test_values:
            end = self.mock_foo_obj.end
            duration = self.mock_foo_obj.duration

            self.mock_foo_obj.start = test_value

            self.assertEqual(
                self.mock_foo_obj.start,
                self.mock_foo_obj.end - self.mock_foo_obj.duration
            )

            # check if we still have the same end
            self.assertEqual(self.mock_foo_obj.end, end)

            # check if we still have the same duration
            self.assertEqual(self.mock_foo_obj.duration, duration)
    
    def test_start_attribute_is_set_to_None_use_the_default_value(self):
        """testing if setting the start attribute to None will update the
        start to today
        """
        self.mock_foo_obj.start = None
        self.assertEqual(self.mock_foo_obj.start,
                         datetime.datetime(2013, 3, 22, 15, 30))
        self.assertIsInstance(self.mock_foo_obj.start, datetime.datetime)
    
    def test_start_attribute_works_properly(self):
        """testing if the start properly is working properly
        """
        test_value = datetime.datetime(year=2011, month=1, day=1)
        self.mock_foo_obj.start = test_value
        self.assertEqual(self.mock_foo_obj.start, test_value)
    
    def test_end_argument_is_not_a_date_object(self):
        """testing if default values will be for the end attribute used when
        trying to set the due date something other than a datetime.datetime
        object
        """
        test_values = [1, 1.2, "str", ["a", "date"],
                       datetime.timedelta(days=100)]
        
        for test_value in test_values:
            self.kwargs["end"] = test_value
            new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)

            self.assertEqual(new_foo_obj.end,
                             new_foo_obj.start + new_foo_obj.duration)
    
    def test_end_attribute_is_not_a_date_object(self):
        """testing if default values will be used for the end attribute
        when trying to set the end attribute to something other than a
        datetime.datetime object
        """
        test_values = [1, 1.2, "str", ["a", "date"],
                       datetime.timedelta(days=100)]
        
        for test_value in test_values:
            self.mock_foo_obj.end = test_value
            
            self.assertEqual(self.mock_foo_obj.end,
                             self.mock_foo_obj.start +\
                             self.mock_foo_obj.duration)
    
    def test_end_argument_is_tried_to_set_to_a_time_before_start(
    self):
        """testing if end attribute will be updated to
        start + duration when the end argument is given as a value
        which is a date before start
        """

        self.kwargs["end"] = self.kwargs["start"] -\
                                  datetime.timedelta(days=10)

        new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)

        self.assertEqual(new_foo_obj.end,
                         new_foo_obj.start + new_foo_obj.duration)
    
    def test_end_attribute_is_tried_to_set_to_a_time_before_start(
    self):
        """testing if a the due attribute is re calculated from the start
        and duration attributes when the end is tried to be set to a date
        before start
        """
        new_end = self.mock_foo_obj.start - datetime.timedelta(days=10)
        self.mock_foo_obj.end = new_end
        self.assertEqual(self.mock_foo_obj.end,
                         self.mock_foo_obj.start +\
                         self.mock_foo_obj.duration)
    
    def test_end_attribute_is_shifted_when_start_passes_it(self):
        """testing if end attribute will be shifted when the start
        attribute passes it
        """
        time_delta = self.mock_foo_obj.end - self.mock_foo_obj.start
        self.mock_foo_obj.start += 2 * time_delta

        self.assertEqual(
            self.mock_foo_obj.end - self.mock_foo_obj.start,
            time_delta
        )

    def test_duration_argument_is_not_an_instance_of_timedelta_no_problem_if_start_and_end_is_present(self):
        """testing if no error will be raised when the duration argument is not
        an instance of datetime.datetime class when both of the start and end
        arguments are present.
        """
        test_values = [1, 1.2, "10", "10 days"]
        
        # no problem if there are start and end arguments
        for test_value in test_values:
            self.kwargs["duration"] = test_value
            new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)

            # check the value
            self.assertEqual(new_foo_obj.duration,
                             new_foo_obj.end - new_foo_obj.start)

    def test_duration_argument_is_not_an_instance_of_date_when_start_argument_is_missing(self):
        """testing if defaults for the duration attribute will be used  when
        the duration argument is not an instance of datetime.datetime class
        when start argument is also missing
        """
        test_values = [1, 1.2, "10", "10 days"]
        self.kwargs.pop("start")
        for test_value in test_values:
            self.kwargs["duration"] = test_value
            new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)

            self.assertEqual(new_foo_obj.duration,
                             defaults.TASK_DURATION)

    def test_duration_argument_is_not_an_instance_of_date_when_end_argument_is_missing(self):
        """testing if the defaults for the duration attribute will be used when
        the duration argument is not an instance of datetime.datetime class and
        when end argument is also missing
        """
        test_values = [1, 1.2, "10", "10 days"]
        self.kwargs.pop("end")
        for test_value in test_values:
            self.kwargs["duration"] = test_value
            new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)
            self.assertEqual(new_foo_obj.duration,
                             defaults.TASK_DURATION)

    def test_duration_attribute_is_calculated_correctly(self):
        """testing if the duration attribute is calculated correctly
        """
        new_foo_entity = SchedMixFooMixedInClass(**self.kwargs)
        new_foo_entity.start = datetime.datetime(2013, 3, 22, 15, 0)
        new_foo_entity.end = new_foo_entity.start +\
                                  datetime.timedelta(201)

        self.assertEqual(new_foo_entity.duration, datetime.timedelta(201))

    def test_duration_attribute_is_set_to_not_an_instance_of_timedelta(self):
        """testing if duration attribute reset to a calculated value when it is
        set to something other than a datetime.timedelta instance
        """
        test_values = [1, 1.2, "10", "10 days"]

        # no problem if there are start and end arguments
        for test_value in test_values:
            self.mock_foo_obj.duration = test_value

            # check the value
            self.assertEqual(self.mock_foo_obj.duration,
                             self.mock_foo_obj.end -\
                             self.mock_foo_obj.start)

    def test_duration_attribute_expands_then_end_shifts(self):
        """testing if duration attribute is expanded then the end
        attribute is shifted
        """
        end = self.mock_foo_obj.end
        start = self.mock_foo_obj.start
        duration = self.mock_foo_obj.duration

        # change the duration
        new_duration = duration * 10
        self.mock_foo_obj.duration = new_duration

        # duration expanded
        self.assertEqual(self.mock_foo_obj.duration, new_duration)

        # start is not changed
        self.assertEqual(self.mock_foo_obj.start, start)

        # end is postponed
        self.assertEqual(self.mock_foo_obj.end, start + new_duration)

    def test_duration_attribute_contracts_then_end_shifts_back(self):
        """testing if duration attribute is contracted then the end
        attribute is shifted back
        """
        end = self.mock_foo_obj.end
        start = self.mock_foo_obj.start
        duration = self.mock_foo_obj.duration

        # change the duration
        new_duration = duration / 2
        self.mock_foo_obj.duration = new_duration

        # duration expanded
        self.assertEqual(self.mock_foo_obj.duration, new_duration)

        # start is not changed
        self.assertEqual(self.mock_foo_obj.start, start)

        # end is postponed
        self.assertEqual(self.mock_foo_obj.end, start + new_duration)

    def test_duration_is_a_negative_timedelta(self):
        """testing if the duration is a negative timedelta will set the
        duration to 1 days
        """
        start = self.mock_foo_obj.start
        self.mock_foo_obj.duration = datetime.timedelta(-10)
        self.assertEqual(self.mock_foo_obj.duration, datetime.timedelta(1))
        self.assertEqual(self.mock_foo_obj.start, start)

    def test_init_all_parameters_skipped(self):
        """testing if the attributes are initialized to:
        
        start = datetime.datetime.now()
        duration = stalker.conf.defaults.DEFAULT_TASK_DURATION
        end = start + duration
        """
        #self.fail("test is not implemented yet")
        self.kwargs.pop("start")
        self.kwargs.pop("end")
        self.kwargs.pop("duration")
        
        new_foo_entity = SchedMixFooMixedInClass(**self.kwargs)
        
        self.assertIsInstance(new_foo_entity.start, datetime.datetime)
        # can not check for start, just don't want to strugle with the round
        # thing
        #self.assertEqual(new_foo_entity.start,
        #                 datetime.datetime(2013, 3, 22, 15, 30))
        self.assertEqual(new_foo_entity.duration,
                         defaults.TASK_DURATION)
        self.assertEqual(new_foo_entity.end,
                         new_foo_entity.start + new_foo_entity.duration)
    
    def test_init_only_start_argument_is_given(self):
        """testing if the attributes are initialized to:
        
        duration = stalker.conf.defaults.DEFAULT_TASK_DURATION
        end = start + duration
        """
        self.kwargs.pop("end")
        self.kwargs.pop("duration")

        new_foo_entity = SchedMixFooMixedInClass(**self.kwargs)

        self.assertEqual(new_foo_entity.duration, defaults.TASK_DURATION)
        self.assertEqual(new_foo_entity.end,
                         new_foo_entity.start + new_foo_entity.duration)
    
    def test_init_start_and_end_argument_is_given(self):
        """testing if the attributes are initialized to:
        
        duration = end - start
        """
        self.kwargs.pop("duration")
        new_foo_entity = SchedMixFooMixedInClass(**self.kwargs)
        self.assertEqual(new_foo_entity.duration,
                         new_foo_entity.end - new_foo_entity.start)
    
    def test_init_start_and_duration_argument_is_given(self):
        """testing if the attributes are initialized to:
        
        end = start + duration
        """

        self.kwargs.pop("end")

        new_foo_entity = SchedMixFooMixedInClass(**self.kwargs)

        self.assertEqual(new_foo_entity.end,
                         new_foo_entity.start + new_foo_entity.duration)
    
    def test_init_all_arguments_are_given(self):
        """testing if the attributes are initialized to:
        
        duration = end - start
        """
        new_foo_entity = SchedMixFooMixedInClass(**self.kwargs)
        self.assertEqual(new_foo_entity.duration,
                         new_foo_entity.end - new_foo_entity.start)
    
    def test_init_end_and_duration_argument_is_given(self):
        """testing if the attributes are initialized to:
        
        start = end - duration
        """
        self.kwargs.pop("start")
        new_foo_entity = SchedMixFooMixedInClass(**self.kwargs)
        self.assertEqual(new_foo_entity.start,
                         new_foo_entity.end - new_foo_entity.duration)
    
    def test_init_only_end_argument_is_given(self):
        """testing if the attributes are initialized to:
        
        duration = stalker.conf.defaults.DEFAULT_TASK_DURATION
        start = end - duration
        """
        self.kwargs.pop("duration")
        self.kwargs.pop("start")
        new_foo_entity = SchedMixFooMixedInClass(**self.kwargs)
        self.assertEqual(new_foo_entity.duration,
                         defaults.TASK_DURATION)
        self.assertEqual(new_foo_entity.start,
                         new_foo_entity.end - new_foo_entity.duration)
    
    def test_init_only_duration_argument_is_given(self):
        """testing if the attributes are initialized to:
        
        start = datetime.date.today()
        end = start + duration
        """
        self.kwargs.pop("end")
        self.kwargs.pop("start")
        
        new_foo_entity = SchedMixFooMixedInClass(**self.kwargs)

        # just check if it is an instance of datetime.datetime
        self.assertIsInstance(new_foo_entity.start, datetime.datetime)
        # can not check for start
        #self.assertEqual(new_foo_entity.start,
        #                 datetime.datetime(2013, 3, 22, 15, 30))
        self.assertEqual(new_foo_entity.end,
                         new_foo_entity.start + new_foo_entity.duration)
    
    def test_resolution_argument_skipped(self):
        """testing if the resolution attribute will be set to the default value
        from the defaults.TIME_RESOLUTION if resolution argument is skipped
        """
        try:
            self.kwargs.pop('resolution')
        except KeyError:
            pass
        
        new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)
        self.assertEqual(new_foo_obj.resolution, defaults.TIME_RESOLUTION)
    
    def test_resolution_argument_is_None(self):
        """testing if the resolution attribute will be set to the default value
        from the defaults.TIME_RESOLUTION if resolution argument is None
        """
        self.kwargs['resolution'] = None
        new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)
        self.assertEqual(new_foo_obj.resolution, defaults.TIME_RESOLUTION)
    
    def test_resolution_attribute_is_set_to_None(self):
        """testing if the resolution attribute will be set to the default value
        from the defaults.TIME_RESOLUTION if it is set to None
        """
        self.kwargs['resolution'] = datetime.timedelta(minutes=5)
        new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)
        # check start conditions
        self.assertEqual(new_foo_obj.resolution, self.kwargs['resolution'])
        new_foo_obj.resolution = None
        self.assertEqual(new_foo_obj.resolution, defaults.TIME_RESOLUTION)
    
    def test_resolution_argument_is_not_a_timedelta_instance(self):
        """testing if a TypeError will be raised when the resolution argument
        is not a datetime.timedelta instance
        """
        self.kwargs['resolution'] = 'not a timedelta instance'
        self.assertRaises(TypeError, SchedMixFooMixedInClass, **self.kwargs)
    
    def test_resolution_attribute_is_not_a_timedelta_instance(self):
        """testing if a TypeError will be raised when the resolution attribute
        is not a datetime.timedelta instance
        """
        new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)
        self.assertRaises(TypeError, setattr, new_foo_obj, 'resolution',
                          'not a timedelta instance')
    
    def test_resolution_argument_is_working_properly(self):
        """testing if the resolution argument value is passed to resolution
        attribute correctly
        """
        self.kwargs['resolution'] = datetime.timedelta(minutes=5)
        new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)
        self.assertEqual(new_foo_obj.resolution, self.kwargs['resolution'])
    
    def test_resolution_attribute_is_working_properly(self):
        """testing if the resolution attribute is working properly
        """
        new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)
        res = new_foo_obj
        new_res = datetime.timedelta(hours=1, minutes=30)
        self.assertNotEqual(res, new_res)
        new_foo_obj.resolution = new_res
        self.assertEqual(new_foo_obj.resolution, new_res)
    
    def test_start_end_and_duration_values_are_rounded_to_the_defined_resolution_argument(self):
        """testing if the start and end dates are rounded to the given
        resolution
        """
        self.kwargs['start'] = datetime.datetime(2013,3,22,02,38,55,531)
        self.kwargs['end'] = datetime.datetime(2013,3,24,16,46,32,102)
        self.kwargs['resolution'] = datetime.timedelta(minutes=5)
        new_foo_obj = SchedMixFooMixedInClass(**self.kwargs)
        # check the start
        expected_start = datetime.datetime(2013,3,22,02,40)
        self.assertEqual(new_foo_obj.start, expected_start)
        # check the end
        expected_end = datetime.datetime(2013,3,24,16,45)
        self.assertEqual(new_foo_obj.end, expected_end)
        # check the duration
        self.assertEqual(new_foo_obj.duration, expected_end - expected_start)
    
