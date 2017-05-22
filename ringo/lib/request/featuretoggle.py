#!/usr/bin/env python
# -*- coding: utf-8 -*-


class FeatureToggle(object):

    """FeatureToggle will give access to the configuration of feature
    toggle configuration in the config file. Feature can be configured
    usind *feature.name* config variables in the ini file.

    To enable a feature you the feature must be set to *true* Any other
    value will evaluate to False which means the feature is not
    enabled."""

    def __init__(self, settings):
        self.settings = settings

    def __getattr__(self, name):
        return self.settings.get("feature.%s" % name) == "true"
