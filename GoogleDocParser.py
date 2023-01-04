import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def getElements(line):
    return line.get('paragraph').get('elements')[0]

def getLineText(line):
    return getElements(line).get('textRun').get('content').replace('\n', '')

# can be 'italic', 'bold' etc.
def getLineStyle(line):
    return getElements(line).get('textRun').get('textStyle')

def lineIsBold(line):
    if 'bold' in getLineStyle(line):
        return True
    return False

def lineIsItalic(line):
    if 'italic' in getLineStyle(line):
        return True
    return False

# can be 'NORMAL_TEXT', 'HEADING_1' etc.
def getLineParagraphStyle(line):
    return line.get('paragraph').get('paragraphStyle').get('namedStyleType')

class GoogleDocumentParser:

    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

    def __init__(self, gdoc_id):
        self.gdoc_id = gdoc_id
        self.gdoc = None

        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            #Save the credits ('token.json') for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('docs', 'v1', credentials=creds)
            self.gdoc = service.documents().get(documentId=self.gdoc_id).execute()

        except HttpError as err:
            print(err)

    def getLines(self):
        return self.gdoc.get('body').get('content')

    def getText(self):
        textLines = []
        for line in self.getLines():
            if 'paragraph' not in line:
                continue
            else:
                textLines.append(line.getElements.get('textRun').get('content').replace('\n', ''))
        return textLines


if __name__ == '__main__':
    GDocPars = GoogleDocumentParser('1tzZT1SXjd1na6BiXkAtlpvP4SEsCqx1Z_cLJvt3cEFc')
    print('The title of the document is: {}'.format(GDocPars.gdoc.get('title')))
    if GDocPars.gdoc is not None:
        t = GDocPars.getLines()
        for i in t:
            if 'paragraph' not in i:
                continue
            print(getLineText(i))
            print(getLineStyle(i))
            print(getLineParagraphStyle(i))
            print()
