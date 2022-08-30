import boto3
# Amazon Textract client
textract = boto3.client('textract')

def transcribe(documentName):
    # Read document content
    with open(documentName, 'rb') as document:
        imageBytes = bytearray(document.read())

    # Call Amazon Textract
    return textract.detect_document_text(Document={'Bytes': imageBytes})

