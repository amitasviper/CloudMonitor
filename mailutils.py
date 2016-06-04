import smtplib
import base64

def sendEmail(to_list, mData):
    data = '\n' + mData + '\n'
    print "\n\n\nSending mail with data : ", data,"\n\n\n"
    try:
        server = smtplib.SMTP('smtp.gmail.com', 25)
        server.starttls()
        server.login('shankarsharma667@gmail.com', base64.b64decode('V2hvQGFyZTF5b3U='))
        for id in to_list:
            server.sendmail('shankarsharma667@gmail.com', id, data)
        server.quit()
        print "Mail sent successfully"
    except:
        print "Error in sending email"

if __name__ == "__main__":
    sendEmail('amitasviper@gmail.com', 'Sample text data')
