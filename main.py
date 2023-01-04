import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

# The ID of a sample document.
DOCUMENT_ID = '1tzZT1SXjd1na6BiXkAtlpvP4SEsCqx1Z_cLJvt3cEFc'

def read_paragraph_element(element):
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')

# style_to_look_for can be 'bold', or 'italic' etc.
def read_paragraph_element_style(element, style_to_look_for):
    text_run = element.get('textRun')
    if not text_run:
        return ''
    else:
        style = text_run.get('textStyle')
        if style.get(style_to_look_for):
            return text_run.get('content')
        return ''

def getLines(doc):
    return doc.get('body').get('content')

def getElements(line):
    return line.get('paragraph').get('elements')[0]

def lineIsBold(line):
    t = getElements(line).get('textRun').get('textStyle')
    if t.get('bold'):
        return True
    return False

def lineIsItalic(line):
    t = getElements(line).get('textRun').get('textStyle')
    if t.get('italic'):
        return True
    return False

def getTextStyle(line):
    return line.get('paragraph').get('paragraphStyle').get('namedStyleType')
    # can be 'NORMAL_TEXT', 'HEADING_1' etc

def getTextFromLine(line):
    return getElements(line).get('textRun').get('content').replace('\n', '')

if __name__ == '__main__':
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=DOCUMENT_ID).execute()

        #print('The title of the document is: {}'.format(document.get('title')))

        QOAEs = []
        curr_q = []
        curr_o = []
        curr_a = []
        curr_e = []
        isQ = False

        lines = getLines(document)
        for l in lines:
            if 'paragraph' not in l:
                continue
            test = l.get('paragraph').get('elements')[0].get('textRun').get('content')

            if getTextStyle(l) == 'NORMAL_TEXT':

                if len(getTextFromLine(l)) <= 1:
                    isQ = True

                    if curr_q:
                        QOAEs.append({
                            'Q': curr_q,
                            'O': curr_o,
                            'A': curr_a,
                            'E': curr_e
                        })
                        curr_q = []
                        curr_o = []
                        curr_a = []
                        curr_e = []

                    continue
                if isQ:
                    curr_q.append(getTextFromLine(l))
                    isQ = False
                    continue

                if not lineIsItalic(l):
                    curr_o.append(getTextFromLine(l))
                if lineIsBold(l):
                    curr_a.append(getTextFromLine(l))
                if lineIsItalic(l):
                    curr_e.append(getTextFromLine(l))

        for i in QOAEs:
            print(i)

        with open('text2anki.txt', 'w') as f:
            lines_to_write = []

            for i in QOAEs:
                temp = ''
                temp += ''.join(i.get('Q'))
                temp += '<br><br>'
                if len(i.get('O')) >= 2:
                    temp += '<br>'.join(i.get('O'))
                temp += ''.join('; ')
                temp += '<br>'.join(i.get('A'))
                temp += ''.join('; ')
                if i.get('E'):
                    temp += '<br>'.join(i.get('E'))
                lines_to_write.append(temp)
                temp = ''

            for line in lines_to_write:
                f.write(line)
                f.write('\n')

    except HttpError as err:
        print(err)
