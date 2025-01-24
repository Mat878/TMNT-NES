class Data:
     """Class used to store health and points of player"""
     def __init__(self, ui):
         self.ui = ui
         self._points = 0
         self._health = 16
         self.ui.create_health(self._health)

         self.current_level = 0

     @property
     def points(self):
         return self._points

     @points.setter
     def points(self, value):
         self._points = value
         self.ui.show_points(int(value))

     @property
     def health(self):
         return self._health

     @health.setter
     def health(self, value):
         self._health = value
         self.ui.create_health(int(value))
