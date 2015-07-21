import web

"""
This is model module for web.py that can serve strings as files and 
upload files as strings.
"""

urls = ('/upload', 'Upload',
        '/download', 'Download',
        '/bob', 'Bob'

)

class Upload:
    def GET(self):
        return """<html><head></head><body>
<form method="POST" enctype="multipart/form-data" action="">
<input type="file" name="myfile" />
<br/>
<input type="submit" />
</form>
</body></html>"""

    def POST(self):
        wi = web.input()
        f = wi['myfile']
        web.header('Content-type','text/html')
        web.header('Transfer-Encoding','chunked')
        return f #this is a string
        
        # x = web.input(myfile={})
        # web.debug(x['myfile'].filename) # This is the filename
        # web.debug(x['myfile'].value) # This is the file contents
        # web.debug(x['myfile'].file.read()) # Or use a file(-like) object
        # raise web.seeother('/upload')

class Bob:
    def GET(self):
        bob = "hi there"
        return bob

class Download:
    def GET(self):
        output="""<!DOCTYPE html>
        <html><head></head><body>
        <a href="/bob" download="bob.txt">Download</a>
        </body></html>"""
        return output
    
if __name__ == "__main__":
   app = web.application(urls, globals()) 
   app.run()
