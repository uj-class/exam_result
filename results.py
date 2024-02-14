from http.server import  BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from jinja2 import Template
from db_utils import get_result
from urllib.parse import urlparse, parse_qs, urlsplit


class MyHandler(BaseHTTPRequestHandler):
    def render_result_html(self):
        file_path = 'result.html'  # Change this to your file's path
        with open(file_path, 'r') as file:
            html_template = file.read()
        template = Template(html_template)
        return template.render()

    def render_output_html(self, student_data):
        file_path = 'output.html'  # Change this to your file's path
        with open(file_path, 'r') as file:
            html_template = file.read()
        template = Template(html_template)
        return template.render(student_data=student_data)
    
    def render_json(self, json_data):
        # Sends a JSON response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json_data.encode())

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        student_id = query_components.get('student_id', [None])[0]
        exam_id = query_components.get('exam_id', [None])[0]


        # Use urlsplit to ignore parameters when comparing paths
        path_without_params = urlsplit(self.path).path

        if path_without_params == '/result_template':
            # Send blank form HTML
            html_content = self.render_result_html()
            self.wfile.write(html_content.encode())

        elif path_without_params == '/json_template':
            # Handle JSON template request
            if exam_id is None or student_id is None:
                # If either student_id or exam_id is missing, send an error response
                error_response = '{"error": "Both student_id and exam_id are required."}'
                self.render_json(error_response)
            else:
                # Get result data
                list_data = get_result(student_id, exam_id)

                # Constructing student_data
                student_data = {
                    'id': student_id,
                    'name': list_data[0][0] if list_data else '',  # Assuming name is the same in all entries
                    'semester': exam_id,
                    'courses': [],
                }

                # Adding courses to student_data
                for course in list_data:
                    student_data['courses'].append({
                        'id': course[1],
                        'name': course[2],
                        'grade': course[3]
                    })

                # Render JSON response with student details
                self.render_json(str(student_data))
    
def run():
    print('Starting server...')
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, MyHandler)
    print('Server started!')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
