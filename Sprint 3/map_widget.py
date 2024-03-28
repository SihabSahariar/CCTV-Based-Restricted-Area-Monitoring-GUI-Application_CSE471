import os
from PyQt5.QtCore import Qt, QUrl, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMessageBox, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel

class MarkerModel(QObject):
    markerAdded = pyqtSignal(float, float, float, str, str)
    rotationUpdated = pyqtSignal(float, str)
    deleteMarker = pyqtSignal(str)
    deletedResponse = pyqtSignal(str)
    searchedLoaction = pyqtSignal(str)

    @pyqtSlot(float, float, float, str, str)
    def addMarker(self, latitude, longitude, rotation_angle, camera_name, ip_address):
        self.markerAdded.emit(latitude, longitude, rotation_angle, camera_name, ip_address)

    @pyqtSlot(float, str)
    def updateRotation(self, angle, camera_name):
        self.rotationUpdated.emit(angle, camera_name)
    
    @pyqtSlot(str)
    def updateDelete(self, camera_name):
        self.deleteMarker.emit(camera_name)
    
    @pyqtSlot(str)
    def deleteResponse(self, camera_name):
        self.deletedResponse.emit(camera_name)

    @pyqtSlot(str)
    def updateSearched(self, searched_location):
        self.searchedLoaction.emit(searched_location)


class MapDisplay(QWidget):
    changeDashboardWindowCheckboxStatus = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.selected_camera_id = None
        self.selected_camera_for_deletion = None
        self.map_data = []#CameraMapDataQuery.fetchAll(self)
        # print("Map data: ", self.map_data)
        self.coordinates = []

        layout = QVBoxLayout()

        script_dir = os.path.dirname(os.path.abspath(__file__))

        self.web_view = QWebEngineView(self)
        self.searched_location_label = QLabel()
        self.searched_location_label.setMaximumHeight(25)
        self.searched_location_label.setStyleSheet("""background: black; color: white; font-weight: normal; font-size: 15px; border: none;""")
        layout.addWidget(self.searched_location_label)
        layout.addWidget(self.web_view)

        html_file_path = os.path.join(script_dir, "map.html")
        self.web_view.setUrl(QUrl.fromLocalFile(html_file_path))

        self.web_channel = QWebChannel(self)
        self.web_view.page().setWebChannel(self.web_channel)

        self.marker_model = MarkerModel()
        self.web_channel.registerObject("markerModel", self.marker_model)

        # Connect slots for marker click event and rotation update
        self.marker_model.markerAdded.connect(self.markerAdded)
        # self.marker_model.rotationUpdated.connect(self.rotationUpdated)
        # self.marker_model.deleteMarker.connect(self.updateDeleteCameraFromMap)
        # self.marker_model.deletedResponse.connect(self.updateMapTableForDelete)
        self.marker_model.searchedLoaction.connect(self.updateSearchLocationLabel)

        # Connect the loadFinished signal to the slot
        self.web_view.loadFinished.connect(self.onLoadFinished)

        self.setLayout(layout)

    def onLoadFinished(self, ok):
        if ok:
            # Set the map data after the HTML has finished loading
            # self.coordinates=[[],[],[]]
            # Some example data of latitude, longitude, rotation angle, camera name, and IP address
            self.coordinates = [[6.5244, 3.3792, 0, "Camera 1", "192.168.0.1"], [7.5244, 8.3792, 0, "Camera 2", "192.168.0.2"], [9.5244, 10.3792, 0, "Camera 3", "192.168.0.3"]]
            set_map_data_script = f"setMapData({self.coordinates});"
            self.web_view.page().runJavaScript(set_map_data_script)
        else:
            print("Failed to load HTML")

    @pyqtSlot(float, float, float, str, str)
    def markerAdded(self, latitude="5.674", longitude="8.66", rotation_angle=30, camera_name="Dummy", ip_address="127.0.0.1"):
        # Add the marker to the map
        add_marker_script = f"addMarker({latitude}, {longitude}, {rotation_angle}, '{camera_name}', '{ip_address}');"
        self.web_view.page().runJavaScript(add_marker_script)
        print("Marker added: ", latitude, longitude, rotation_angle, camera_name, ip_address)
        # if camera_name is not None or camera_name != "":
        #     self.changeDashboardWindowCheckboxStatus.emit(False)
        #     camera_data = CameraDataQuery.fetchOneByName(self, camera_name)
        #     if camera_data and camera_data != "Camera not found!":
        #         camera_already_in_map_list = False
        #         map_data = CameraMapDataQuery.fetchAll(self)
        #         for map_single in map_data:
        #             if map_single['camera']['camera_name'] == camera_data.camera_name:
        #                 camera_already_in_map_list = True
        #                 self.show_notification("Warning", "Camera is already in map list!")
        #                 break
        #         if not camera_already_in_map_list:
        #             new_marker = CameraMapDataQuery.insert(self, camera_data.id, longitude, latitude, rotation_angle)
        #             if new_marker != None:
        #                 self.show_notification("Success", "Camera added to map successfully!")
        #                 self.selected_camera_id = None
        #                 camera_already_in_map_list = False
                        
    # @pyqtSlot(float, str)
    # def rotationUpdated(self, angle, camera_name):
    #     if camera_name != None:
    #         camera_data = CameraDataQuery.fetchOneByName(self, camera_name)
    #         if camera_data and camera_data != "Camera not found!":
    #             map_data = CameraMapDataQuery.fetchAll(self)
    #             for map_single in map_data:
    #                 if map_single['camera']['camera_name'] == camera_data.camera_name:
    #                     CameraMapDataQuery.update(self, map_single['id'], map_single['longitude'], map_single['latitude'], angle)
    #                     break
    
    # @pyqtSlot(str)
    # def updateDeleteCameraFromMap(self, camera_name):
    #     if camera_name != None:
    #         self.selected_camera_for_deletion = camera_name


    # @pyqtSlot(str)
    # def updateMapTableForDelete(self, camera_name):
    #     if camera_name != None:
    #         cam_data = CameraDataQuery.fetchOneByName(self, camera_name)
    #         if cam_data and cam_data != "Camera not found!":
    #             print("Cmaera data on map maker delete: ", cam_data.id)
    #             map_data = CameraMapDataQuery.fetchByCameraId(self, cam_data.id)
    #             if map_data:
    #                 deleted_map_data = CameraMapDataQuery.remove(self, map_data['id'])
    #                 if deleted_map_data:
    #                     self.show_notification("Warning", "Map data deleted!")
    
    @pyqtSlot(str)
    def updateSearchLocationLabel(self, label_txt):
        self.searched_location_label.setText(f"{label_txt}")

    def setTerrainView(self):
        # Call the JavaScript function to set the terrain view
        self.web_view.page().runJavaScript("setMapView('terrain');")

    def setSatelliteView(self):
        # Call the JavaScript function to set the satellite view
        self.web_view.page().runJavaScript("setMapView('satellite');")

    def deleteSelectedMarker(self):
        if self.selected_camera_for_deletion is not None:
            # Call a JavaScript function to delete the marker based on the camera ID
            delete_marker_script = f"deleteMarker('{self.selected_camera_for_deletion}');"
            self.web_view.page().runJavaScript(delete_marker_script)
            
            # Optionally, update your internal data structures to reflect the deletion
            # For example, you might want to remove the marker from self.coordinates
            # and update the map accordingly.

            # Clear the selected camera ID
            self.selected_camera_for_deletion = None
        
    
    def show_notification(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.exec_()
            


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MapDisplay()
    window.show()
    sys.exit(app.exec_())