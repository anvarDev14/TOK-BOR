from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = '1vGcWE_zMm_viht2Jlv2GaDT3fbIj9qldgAlyXp4lklY'  # Замените на ID вашей таблицы
DRIVE_FOLDER_ID = '1dw47VRFcxCw6SSsQKD7rwJKGQcncJDfi'  # Замените на ID папки в Google Drive

# Service Account bilan avtorizatsiya
try:
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES
    )
    logger.debug("Service Account avtorizatsiyasi muvaffaqiyatli")
except Exception as e:
    logger.error(f"Service Account avtorizatsiyasida xatolik: {str(e)}")
    raise

sheets_service = build('sheets', 'v4', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)


# Google Sheets’ga ma’lumot qo‘shish funksiyasi
def append_to_sheet(values):
    try:
        body = {'values': [values]}
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        logger.debug("Ma'lumotlar Google Sheets'ga muvaffaqiyatli yozildi")
    except Exception as e:
        logger.error(f"Google Sheets'ga yozishda xatolik: {str(e)}")
        raise


# Google Drive’ga foto yuklash funksiyasi
def upload_to_drive(file_path, file_name):
    try:
        logger.debug(f"Google Drive'ga yuklash: {file_name}")
        file_metadata = {
            'name': file_name,
            'parents': [DRIVE_FOLDER_ID]
        }
        media = MediaFileUpload(file_path)
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file.get('id')
        logger.debug(f"Fayl yuklandi, ID: {file_id}")

        # Faylga umumiy ruxsat berish
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        logger.debug("Faylga umumiy ruxsat berildi")

        return f"https://drive.google.com/file/d/{file_id}/view"
    except Exception as e:
        logger.error(f"Google Drive'ga yuklashda xatolik: {str(e)}")
        logger.error(f"Xatolik stack trace: {traceback.format_exc()}")
        raise