import io
import time
from enum import Enum
from typing import Callable, List, Optional, Tuple
from PyQt6.QtCore import QBuffer, QByteArray, QThread, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QImage
from PyQt6.QtWidgets import (
    QDialog,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from ffmpeg.nodes import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build

from components.message_dialog import CustomInformationDialog, CustomCriticalDialog
from components.loading_dialog import LoadingDialog
from preload import ICON_DIR

UPLOAD_ICON = os.path.join(ICON_DIR, "upload.svg")
DRIVE_ICON = os.path.join(ICON_DIR, "drive.svg")


class ResourceType(Enum):
    IMAGE = "image"
    VIDEO = "video"


class UploadResource:
    def __init__(
        self,
        resource_type: ResourceType,
        image: Optional[QImage] = None,
        video_url: Optional[str] = None,
    ) -> None:
        self.resource_type = resource_type
        self.image = image
        self.video_url = video_url


class ResourceConverter(QThread):
    resource_converted = pyqtSignal(bytes, ResourceType)
    resource_conversion_error = pyqtSignal(str)

    def __init__(self, resource: UploadResource):
        super().__init__()
        self.__resource = resource

    def run(self) -> None:
        if self.__resource.resource_type == ResourceType.IMAGE:
            image = self.__resource.image
            assert image is not None
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QBuffer.OpenModeFlag.WriteOnly)
            image.save(buffer, "PNG")
            buffer.close()
            byte_array = byte_array.data()
            self.resource_converted.emit(byte_array, ResourceType.IMAGE)
            return

        if self.__resource.resource_type == ResourceType.VIDEO:
            video_url = self.__resource.video_url
            assert video_url is not None
            if os.path.exists(video_url):
                with open(video_url, "rb") as f:
                    self.resource_converted.emit(f.read(), ResourceType.VIDEO)
                return

            self.resource_conversion_error.emit(f"File not found: {video_url}")
            return

        self.resource_conversion_error.emit("Invalid resource type")


class UploadButton(QPushButton):
    def __init__(
        self,
        on_upload_event: Callable[[], UploadResource],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(QIcon(UPLOAD_ICON), "")

        self.setToolTip("Upload to Cloud")
        self.clicked.connect(self.__upload)
        self.__parent = parent
        self.__on_upload_event = on_upload_event

    def __upload(self) -> None:
        self.__loading_dialog = LoadingDialog(self.__parent)
        resource = self.__on_upload_event()
        converter = ResourceConverter(resource)
        converter.resource_converted.connect(self.__on_complete)
        converter.resource_conversion_error.connect(self.__on_error)
        converter.start()
        self.__loading_dialog.show_loading()

    def __on_complete(self, byte_array: bytes, rtype: ResourceType) -> None:
        if self.__loading_dialog:
            self.__loading_dialog.close()
        self.__cloud_uploader = CloudUploader(byte_array, rtype, self.__parent)
        self.__cloud_uploader.show()

    def __on_error(self, message: str) -> None:
        if self.__loading_dialog:
            self.__loading_dialog.close()
        CustomCriticalDialog("Error", message, self.__parent).exec()


class Message:
    def __init__(self, title: str, message: str):
        self.title = title
        self.message = message

    @staticmethod
    def dummy() -> "Message":
        return Message("", "")


class CloudUploader(QDialog):
    def __init__(
        self,
        resource: bytes,
        rtype: ResourceType,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.__parent = parent
        self.__resource = resource
        self.__rtype = rtype
        self.setWindowTitle("Upload to Cloud")
        self.setModal(True)

        layout = QVBoxLayout()

        self.__drive_uploader = DriveUploader()
        self.__drive_upload_btn = QPushButton(
            QIcon(DRIVE_ICON), "Upload to Google Drive"
        )
        self.__drive_upload_btn.clicked.connect(self.__on_drive_upload)

        layout.addWidget(self.__drive_upload_btn)

        self.setLayout(layout)
        self.setFixedSize(400, 100)

    def __on_drive_upload(self):
        self.close()

        saved_time = time.strftime("%Y%m%d%H%M%S")

        ext = ""
        if self.__rtype == ResourceType.IMAGE:
            ext = "png"
            rtype = "image/png"
        elif self.__rtype == ResourceType.VIDEO:
            ext = "mp4"
            rtype = "video/mp4"
        else:
            raise ValueError("Invalid resource type")

        saved_filename = f"becap_upload_{saved_time}.{ext}"

        self.__drive_uploader.upload_data(
            self.__resource,
            saved_filename,
            rtype,
            self.__on_cancel_upload,
            self.__on_uploading,
            self.__on_upload_complete,
            self.__on_upload_error,
            self.__parent,
        )

    def __on_cancel_upload(self):
        self.show()

    def __on_uploading(self):
        self.__loading_dialog = LoadingDialog(self.__parent)
        self.__loading_dialog.show_loading()

    def __on_upload_complete(self, message: Message):
        if self.__loading_dialog:
            self.__loading_dialog.close()
        CustomInformationDialog(message.title, message.message, self.__parent).exec()

    def __on_upload_error(self, message: Message):
        if self.__loading_dialog:
            self.__loading_dialog.close()
        CustomCriticalDialog(message.title, message.message, self.__parent).exec()


class DriveFolder:
    def __init__(self, id: str, name: str, path: str):
        self.id: str = id
        self.name: str = name
        self.path: str = path


class DriveFolderPicker(QDialog):
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self.selected_folder_id = "root"
        self.selected_path = "/My Drive"
        self.setWindowTitle("Select Google Drive Folder")
        self.setFixedSize(400, 500)
        self.__setup_ui()
        self.__load_folders()

    def __setup_ui(self):
        layout = QVBoxLayout()

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Folders")
        self.tree.itemExpanded.connect(self.__load_subfolders)
        self.tree.itemClicked.connect(self.__folder_selected)
        layout.addWidget(self.tree)

        # Buttons
        button_layout = QVBoxLayout()
        self.select_btn = QPushButton("Select")
        self.select_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.select_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def __load_folders(self):
        # Add root folder
        root_item = QTreeWidgetItem(self.tree)
        root_item.setText(0, "My Drive")
        root_item.setData(
            0, Qt.ItemDataRole.UserRole, {"id": "root", "path": "/My Drive"}
        )

        # Add placeholder child to show expand arrow
        QTreeWidgetItem(root_item)
        self.tree.addTopLevelItem(root_item)

    def __load_subfolders(self, parent_item: QTreeWidgetItem):
        # Remove placeholder if exists
        if parent_item.childCount() == 1:
            item = parent_item.child(0)
            assert item is not None
            if item.text(0) == "":
                parent_item.removeChild(item)

        folder_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
        parent_id = folder_data["id"]
        parent_path = folder_data["path"]

        try:
            results = (
                self.service.files()
                .list(
                    q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'",
                    spaces="drive",
                    fields="files(id, name)",
                    orderBy="name",
                )
                .execute()
            )

            for folder in results.get("files", []):
                item = QTreeWidgetItem(parent_item)
                item.setText(0, folder["name"])
                folder_path = f"{parent_path}/{folder['name']}"
                item.setData(
                    0,
                    Qt.ItemDataRole.UserRole,
                    {"id": folder["id"], "path": folder_path},
                )
                # Add placeholder child to show expand arrow
                QTreeWidgetItem(item)

        except Exception as e:
            CustomCriticalDialog(
                "Error", f"Failed to load folders: {str(e)}", self
            ).exec()

    def __folder_selected(self, item: QTreeWidgetItem, column: int):
        folder_data = item.data(0, Qt.ItemDataRole.UserRole)
        self.selected_folder_id = folder_data["id"]
        self.selected_path = folder_data["path"]


class DriveUploader:
    SCOPES: List[str] = ["https://www.googleapis.com/auth/drive"]
    TOKEN_FILE: str = "token.json"
    CREDENTIALS_FILE: str = "credentials.json"

    def __init__(self):
        self.__upload_worker: Optional[UploadWorker] = None

    def upload_data(
        self,
        data: bytes,
        filename: str,
        mime_type: str,
        on_cancel_upload: Callable[[], None],
        on_uploading: Callable[[], None],
        on_upload_complete: Callable[[Message], None],
        on_upload_error: Callable[[Message], None],
        parent: Optional[QWidget] = None,
    ) -> None:
        credentials, error = self.__load_credentials()
        if not credentials:
            on_upload_error(error)
            return

        service = build("drive", "v3", credentials=credentials)

        folder_picker = DriveFolderPicker(service, parent)
        if folder_picker.exec() != QDialog.DialogCode.Accepted:
            on_cancel_upload()
            return

        self.__start_upload(
            service,
            data,
            filename,
            mime_type,
            folder_picker.selected_folder_id,
            on_uploading,
            on_upload_complete,
            on_upload_error,
        )

    def __load_credentials(
        self,
    ) -> Tuple[Credentials | None, Message]:  # (credentials, error_message)
        try:
            credentials = None
            if os.path.exists(self.TOKEN_FILE):
                with open(self.TOKEN_FILE, "r") as token:
                    credentials = Credentials.from_authorized_user_file(
                        self.TOKEN_FILE, self.SCOPES
                    )

            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    if not os.path.exists(self.CREDENTIALS_FILE):
                        return (
                            None,
                            Message(
                                "Configuration Error",
                                f"Missing {self.CREDENTIALS_FILE}. Please obtain it from Google Cloud Console.",
                            ),
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.CREDENTIALS_FILE, self.SCOPES
                    )

                    cred = flow.run_local_server(port=0)
                    assert isinstance(cred, Credentials)
                    credentials = cred

                with open(self.TOKEN_FILE, "w") as token:
                    token.write(credentials.to_json())

            return credentials, Message.dummy()
        except Exception as e:
            return None, Message("Authentication Error", str(e))

    def __start_upload(
        self,
        service,
        data: bytes,
        filename: str,
        mime_type: str,
        folder_id: str,
        on_uploading: Callable[[], None],
        on_upload_complete: Callable[[Message], None],
        on_upload_error: Callable[[Message], None],
    ) -> None:
        self.__upload_worker = UploadWorker(
            service,
            data,
            filename,
            folder_id,
            mime_type,
        )

        self.__upload_worker.upload_completed.connect(on_upload_complete)
        self.__upload_worker.upload_error.connect(on_upload_error)

        self.__upload_worker.start()
        on_uploading()


class UploadWorker(QThread):
    upload_completed = pyqtSignal(Message)
    upload_error = pyqtSignal(Message)

    def __init__(
        self,
        service,
        data: bytes,
        filename: str,
        folder_id: str,
        mime_type: str,
    ):
        super().__init__()
        self.__data = data
        self.__filename = filename
        self.__folder_id = folder_id
        self.__mime_type = mime_type
        self.__service = service

    def __upload_data(self) -> Tuple[str, str]:
        data_bytes = self.__data
        fh = io.BytesIO(data_bytes)
        file_metadata = {"name": self.__filename, "parents": [self.__folder_id]}
        media = MediaIoBaseUpload(fh, mimetype=self.__mime_type, resumable=True)
        response = (
            self.__service.files()
            .create(body=file_metadata, media_body=media, fields="id, name, parents")
            .execute()
        )

        file_path = self.__get_file_path(response.get("id"))
        return response.get("id"), file_path

    def __get_file_path(self, file_id: str) -> str:
        """Get the full path of the uploaded file in Drive."""

        def get_folder_name(folder_id):
            if folder_id == "root":
                return "My Drive"
            try:
                folder = (
                    self.__service.files()
                    .get(fileId=folder_id, fields="name")
                    .execute()
                )
                return folder.get("name")
            except Exception:
                return "Unknown Folder"

        path_parts = []
        current_file = (
            self.__service.files().get(fileId=file_id, fields="parents,name").execute()
        )

        path_parts.append(current_file.get("name"))

        parent_id = current_file.get("parents", [None])[0]
        while parent_id:
            folder_name = get_folder_name(parent_id)
            path_parts.append(folder_name)
            if parent_id == "root":
                break
            try:
                parent = (
                    self.__service.files()
                    .get(fileId=parent_id, fields="parents,name")
                    .execute()
                )
                parent_id = parent.get("parents", [None])[0]
            except Exception:
                break

        return "/" + "/".join(reversed(path_parts))

    def run(self) -> None:
        try:
            file_id, file_path = self.__upload_data()
            message = Message(
                "Success",
                f"{self.__filename} uploaded successfully!\nLocation: {file_path}",
            )
            self.upload_completed.emit(message)
        except Exception as e:
            message = Message("Error", str(e))
            self.upload_error.emit(message)
