class Modifier(object):
    """ Base class for modifier objects. Inheriting classes should override `_modify` """
    def modify(self, settings):
        seen = []
        while settings and settings not in seen:
            self._modify(settings)
            seen.append(settings)
            settings = settings.next_settings

    def _modify(self, settings):
        return settings
