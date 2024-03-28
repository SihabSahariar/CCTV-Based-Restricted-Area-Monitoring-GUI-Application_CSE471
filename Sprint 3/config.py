import sys
import configparser
from PyQt5.QtWidgets import *

def read_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    config_values = dict(config["DEFAULT"])
    
    # Convert certain values to their appropriate types if needed
    config_values["maxqueue"] = int(config_values["maxqueue"])
    config_values["skip_frame"] = int(config_values["skip_frame"])
    config_values["max_update_time"] = int(config_values["max_update_time"])

    # Handle record_size when it is in the format (1280,720)
    record_size_str = config_values["record_size"]
    if record_size_str.startswith("(") and record_size_str.endswith(")"):
        record_size_str = record_size_str[1:-1]  # Remove parentheses
        width, height = map(int, record_size_str.split(','))
        config_values["record_size"] = (width, height)
    else:
        config_values["record_size"] = tuple(map(int, record_size_str.split(',')))

    # Rest of the configuration options
    config_values["enable_redis"] = config.getboolean("I/O", "enable_redis")
    config_values["enable_web"] = config.getboolean("I/O", "enable_web")
    config_values["db_insert"] = config.getboolean("I/O", "db_insert")
    config_values["save_img"] = config.getboolean("I/O", "save_img")
    config_values["video_record"] = config.getboolean("I/O", "video_record")
    config_values["translate"] = config.getboolean("I/O", "translate")

    # Additional configuration options from the THRESHOLDS section
    config_values["parking_threshold"] = float(config.get("THRESHOLDS", "parking_threshold"))
    return config_values


def save_config(config_values):
    config = configparser.ConfigParser()
    config.read("config.ini")
    for key, value in config_values.items():
        if isinstance(value, bool):
            value = str(value).lower()  # Convert boolean to lowercase string
        
        if key == "record_size":
            # Convert record_size tuple to string format "(width, height)"
            value = f"({value[0]},{value[1]})"
            print(value)

        if key in ["enable_redis", "enable_web", "db_insert", "save_img", "video_record","translate"]:
            config.set("I/O", key, str(value))
        elif key in ["parking_threshold"]:
            config.set("THRESHOLDS", key, str(value))
        else:
            config.set("DEFAULT", key, str(value))
            
    with open("config.ini", "w") as config_file:
        config.write(config_file)


def create_stylesheet():
    return """
    QWidget {
        background-color:#1d1d1d;;
        font-family: Arial;
    }
    QLabel {
        margin: 10px;
        padding: 5px;
        color: #fff;
        border: 1px solid #ccc;
        border-radius: 5px;
        background-color:rgb(70,70,170);
    }
    QLineEdit {
        margin: 10px;
        padding: 5px;
        color: #fff;
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    QCheckBox {
        margin: 10px;
        padding: 5px;
        color: #fff;
    }
    QPushButton {
        margin: 10px;
        padding: 5px;
        background-color: #007BFF;
        color: #fff;
        border: none;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #0056b3;
    }
    """

class ConfigApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setStyleSheet(create_stylesheet())
        self.input_fields = {}
        self.initUI()
        # self.setFixedSize(700,800)

    def initUI(self):
        self.config_values = read_config()
        layout = QGridLayout()

        row = 0
        for key, value in self.config_values.items():
            # Modify keys: Remove underscores and maintain Capital/Small letter arrangement
            key_label = " ".join(word.capitalize() for word in key.split("_"))
            if key_label == "Maxqueue":
                key_label = "Max Queue"
            elif key_label == "Record Size":
                key_label = "Record Screen Size (Width, Height)"
            elif key_label == "Max Update Time":
                key_label = "Maximum Update Time"
            elif key_label == "Recording Dir":
                key_label = "Recording Directory"
            elif key_label == "Enable Redis":
                key_label = "Enable Redis Service"
            elif key_label == "Enable Web":
                key_label = "Enable Web Service"
            elif key_label == "Db Insert":
                key_label = "Database Insertion"
            elif key_label == "Save Img":
                key_label = "Save Image"
            elif key_label == "Video Record":
                key_label = "Video Record"
            elif key_label == "Translate":
                key_label = "Translate Into Korean"

            label = QLabel(f"{key_label}:")
            if key in ["enable_redis", "enable_web", "db_insert", "save_img", "video_record","translate"]:
                checkbox = QCheckBox()
                checkbox.setChecked(value)
                layout.addWidget(label, row, 0)
                layout.addWidget(checkbox, row, 1)
                self.input_fields[key] = checkbox
            elif key == "record_size":
                # Special handling for "record_size" which is a tuple of two integers
                key_label = "Record Screen Size (Width, Height)"
                label = QLabel(f"{key_label}:")
                input_field_width = QLineEdit(str(value[0]))
                input_field_height = QLineEdit(str(value[1]))
                layout.addWidget(label, row, 0)
                layout.addWidget(input_field_width, row, 1)
                layout.addWidget(input_field_height, row, 2)
                self.input_fields[key] = input_field_width, input_field_height
                row += 1
            else:
                input_field = QLineEdit(str(value))
                layout.addWidget(label, row, 0)
                layout.addWidget(input_field, row, 1)
                self.input_fields[key] = input_field
            row += 1


        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button, row, 0, 1, 3)

        container = QWidget()
        container.setLayout(layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)  # Add the scroll area to the main layout
        self.setLayout(main_layout)
        self.resize(700, 650)


    def save_settings(self):
        for key, input_field in self.input_fields.items():
            if key == "record_size":
                # For record_size, get the width and height from the corresponding QLineEdit fields
                width_input_field, height_input_field = input_field
                width = width_input_field.text()
                height = height_input_field.text()
                self.config_values[key] = (int(width), int(height))
            elif isinstance(input_field, QLineEdit):
                self.config_values[key] = input_field.text()
            elif isinstance(input_field, QCheckBox):
                self.config_values[key] = input_field.isChecked()

        save_config(self.config_values)
        # Show a message after saving
        QMessageBox.information(self, "Settings Saved", "Configuration has been saved successfully. Please restart the application for the changes to take effect.")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigApp()
    window.show()
    sys.exit(app.exec_())

