import boto3
# Amazon Textract client
textract = boto3.client('textract', region_name='ap-south-1')

def transcribe(documentName):
    # Read document content
    with open(documentName, 'rb') as document:
        imageBytes = bytearray(document.read())

    # Call Amazon Textract
    return textract.detect_document_text(Document={'Bytes': imageBytes})

