from typing import List, Optional, Dict, Tuple, Union
from io import BytesIO
from PyQt6.QtWidgets import (
    QPushButton, QFileDialog, QMessageBox, QWidget,
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import QThread, pyqtSignal, QByteArray, Qt
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
import os
import json
import io

class DriveFolder:
    def __init__(self, id: str, name: str, path: str):
        self.id: str = id
        self.name: str = name
        self.path: str = path

class DriveFolderPicker(QDialog):
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self.selected_folder_id = 'root'
        self.selected_path = '/My Drive'
        self.setWindowTitle("Select Google Drive Folder")
        self.resize(400, 500)
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
        root_item.setData(0, Qt.ItemDataRole.UserRole, {'id': 'root', 'path': '/My Drive'})
        
        # Add placeholder child to show expand arrow
        QTreeWidgetItem(root_item)
        self.tree.addTopLevelItem(root_item)

    def __load_subfolders(self, parent_item: QTreeWidgetItem):
        # Remove placeholder if exists
        if parent_item.childCount() == 1 and parent_item.child(0).text(0) == "":
            parent_item.removeChild(parent_item.child(0))
            
        folder_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
        parent_id = folder_data['id']
        parent_path = folder_data['path']

        try:
            results = self.service.files().list(
                q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='files(id, name)',
                orderBy='name'
            ).execute()

            for folder in results.get('files', []):
                item = QTreeWidgetItem(parent_item)
                item.setText(0, folder['name'])
                folder_path = f"{parent_path}/{folder['name']}"
                item.setData(0, Qt.ItemDataRole.UserRole, {'id': folder['id'], 'path': folder_path})
                # Add placeholder child to show expand arrow
                QTreeWidgetItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load folders: {str(e)}")

    def __folder_selected(self, item: QTreeWidgetItem, column: int):
        folder_data = item.data(0, Qt.ItemDataRole.UserRole)
        self.selected_folder_id = folder_data['id']
        self.selected_path = folder_data['path']

class UploadWorker(QThread):
    upload_completed = pyqtSignal(str, str, str)
    upload_error = pyqtSignal(str, str)

    def __init__(self, credentials: Credentials, data: Union[QByteArray, bytes], 
                 filename: str, folder_id: str, mime_type: str):
        super().__init__()
        self.__credentials = credentials
        self.__data = data
        self.__filename = filename
        self.__folder_id = folder_id
        self.__mime_type = mime_type
        self.__service = build('drive', 'v3', credentials=credentials)

    def __upload_data(self) -> Tuple[str, str]:
        if isinstance(self.__data, QByteArray):
            data_bytes = bytes(self.__data)
        else:
            data_bytes = self.__data

        fh = io.BytesIO(data_bytes)

        file_metadata = {
            'name': self.__filename,
            'parents': [self.__folder_id]
        }

        media = MediaIoBaseUpload(
            fh,
            mimetype=self.__mime_type,
            resumable=True
        )

        response = self.__service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, parents'
        ).execute()

        file_path = self.__get_file_path(response.get('id'))
        return response.get('id'), file_path

    def __get_file_path(self, file_id: str) -> str:
        """Get the full path of the uploaded file in Drive."""
        def get_folder_name(folder_id):
            if folder_id == 'root':
                return 'My Drive'
            try:
                folder = self.__service.files().get(fileId=folder_id, fields='name').execute()
                return folder.get('name')
            except:
                return 'Unknown Folder'

        path_parts = []
        current_file = self.__service.files().get(
            fileId=file_id,
            fields='parents,name'
        ).execute()
        
        path_parts.append(current_file.get('name'))
        
        parent_id = current_file.get('parents', [None])[0]
        while parent_id:
            folder_name = get_folder_name(parent_id)
            path_parts.append(folder_name)
            if parent_id == 'root':
                break
            try:
                parent = self.__service.files().get(
                    fileId=parent_id,
                    fields='parents,name'
                ).execute()
                parent_id = parent.get('parents', [None])[0]
            except:
                break

        return '/' + '/'.join(reversed(path_parts))

    def run(self) -> None:
        try:
            file_id, file_path = self.__upload_data()
            self.upload_completed.emit(self.__filename, file_id, file_path)
        except Exception as e:
            self.upload_error.emit(self.__filename, str(e))

class DriveUploader(QDialog):
    SCOPES: List[str] = ['https://www.googleapis.com/auth/drive']
    TOKEN_FILE: str = 'token.json'
    CREDENTIALS_FILE: str = 'credentials.json'

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Upload to Google Drive")
        self.__credentials: Optional[Credentials] = None
        self.__service: Optional[Any] = None
        self.__upload_worker: Optional[UploadWorker] = None
        self.__setup_ui()

    def __setup_ui(self) -> None:
        layout = QVBoxLayout()
        
        # Upload button
        self.__upload_btn = QPushButton("Select Folder and Upload")
        self.__upload_btn.clicked.connect(self.__select_folder_and_upload)
        layout.addWidget(self.__upload_btn)
        
        self.setLayout(layout)
        self.resize(400, 100)

    def upload_data(self, data: Union[QByteArray, bytes], filename: str, mime_type: str) -> None:
        if self.__load_credentials():
            self.__service = build('drive', 'v3', credentials=self.__credentials)
            self.show()
            self.__filename = filename
            self.__data = data
            self.__mime_type = mime_type

    def __load_credentials(self) -> bool:
        try:
            if os.path.exists(self.TOKEN_FILE):
                with open(self.TOKEN_FILE, 'r') as token:
                    self.__credentials = Credentials.from_authorized_user_file(
                        self.TOKEN_FILE, 
                        self.SCOPES
                    )
            
            if not self.__credentials or not self.__credentials.valid:
                if self.__credentials and self.__credentials.expired and self.__credentials.refresh_token:
                    self.__credentials.refresh(Request())
                else:
                    if not os.path.exists(self.CREDENTIALS_FILE):
                        self.__show_error_message(
                            "Configuration Error",
                            f"Missing {self.CREDENTIALS_FILE}. Please obtain it from Google Cloud Console."
                        )
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.CREDENTIALS_FILE, 
                        self.SCOPES
                    )
                    self.__credentials = flow.run_local_server(port=0)
                
                with open(self.TOKEN_FILE, 'w') as token:
                    token.write(self.__credentials.to_json())
            
            return True
        except Exception as e:
            self.__show_error_message("Authentication Error", str(e))
            return False

    def __select_folder_and_upload(self) -> None:
        folder_picker = DriveFolderPicker(self.__service, self)
        if folder_picker.exec() == QDialog.DialogCode.Accepted:
            self.__start_upload(folder_picker.selected_folder_id)

    def __start_upload(self, folder_id: str) -> None:
        self.__upload_worker = UploadWorker(
            self.__credentials,
            self.__data,
            self.__filename,
            folder_id,
            self.__mime_type
        )
        
        self.__upload_worker.upload_completed.connect(self.__handle_upload_complete)
        self.__upload_worker.upload_error.connect(self.__handle_upload_error)
        
        self.__upload_worker.start()
        self.__upload_btn.setEnabled(False)

    def __handle_upload_complete(self, filename: str, file_id: str, file_path: str) -> None:
        self.__show_success_message(
            "Success",
            f"{filename} uploaded successfully!\nLocation: {file_path}"
        )
        self.__upload_btn.setEnabled(True)
        self.accept()

    def __handle_upload_error(self, filename: str, error: str) -> None:
        self.__show_error_message(
            "Upload Error",
            f"Failed to upload {filename}: {error}"
        )
        self.__upload_btn.setEnabled(True)

    def __show_error_message(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def __show_success_message(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)