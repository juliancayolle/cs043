import wsgiref.simple_server
import urllib.parse
import sqlite3
import http.cookies
import random

connection = sqlite3.connect('users.db')
stmt = "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
cursor = connection.cursor()
result = cursor.execute(stmt)
r = result.fetchall()
if (r == []):
    exp = 'CREATE TABLE users (username,password)'
    connection.execute(exp)


def application(environ, start_response):
    headers = [('Content-Type', 'text/html; charset=utf-8')]

    path = environ['PATH_INFO']
    params = urllib.parse.parse_qs(environ['QUERY_STRING'])
    un = params['username'][0] if 'username' in params else None
    pw = params['password'][0] if 'password' in params else None

    if path == '/register' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ?', [un]).fetchall()
        if user:
            start_response('200 OK', headers)
            return ['Sorry, username {} is taken'.format(un).encode()]
        else:
            #[INSERT CODE HERE. Use SQL commands to insert the new username and password into the table that has been created. Print a message saying the username was created successfully]
            #done
            cursor.execute('INSERT INTO users VALUES (?, ?)', [un, pw])
            connection.commit()
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return ['User {} successfully registered. <a href="/account">Account</a>'.format(un).encode()]
    elif path == '/login' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return ['User {} successfully logged in. <a href="/account">Account</a>'.format(un).encode()]
        else:
            start_response('200 OK', headers)
            return ['Incorrect username or password'.encode()]

    elif path == '/logout':
        headers.append(('Set-Cookie', 'session=0; expires=Thu, 01 Jan 1970 00:00:00 GMT'))
        start_response('200 OK', headers)
        return ['Logged out. <a href="/">Login</a>'.encode()]

    elif path == '/account':
        start_response('200 OK', headers)

        if 'HTTP_COOKIE' not in environ:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])
        if 'session' not in cookies:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        [un, pw] = cookies['session'].value.split(':')
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()

        #This is where the game begins. This section of is code only executed if the login form works, and if the user is successfully logged in
        if user:
            correct = 0
            wrong = 0

            if 'HTTP_COOKIE' in environ and 'score' in cookies:
                # [INSERT CODE FOR COOKIES HERE]
                cookies = http.cookies.SimpleCookie()
                cookies.load(environ['HTTP_COOKIE'])
                correct = int(cookies['score'].value.split(':')[0])
                wrong = int(cookies['score'].value.split(':')[1])

            page = '<!DOCTYPE html><html><head><title>Multiply with Score</title></head><body>'
            # [INSERT CODE HERE. If the answer is right, show the ìcorrectî message. If itís wrong, show the ìwrongî message.]
            #done
            if 'factor1' in params and 'factor2' in params and 'answer' in params:
                f1 = int(params['factor1'][0])
                f2 = int(params['factor2'][0])
                user_answer = int(params['answer'][0])
                if user_answer == f1 * f2:
                    page +=  '<p style="background-color: lightgreen">Correct</p>'
                    correct += 1
                else:
                   page += '<p style="background-color: red">Wrong</p>'
                   wrong += 1

            elif 'reset' in params:
                correct = 0
                wrong = 0

            headers.append(('Set-Cookie', 'score={}:{}'.format(correct, wrong)))

            f1 = random.randrange(10) + 1
            f2 = random.randrange(10) + 1
            a = random.randrange(100) + 1
            b = random.randrange(100) + 1
            c = random.randrange(100) + 1
            answer = [f1 * f2, a, b, c]

            page = page + '<h1>What is {} x {}?</h1>'.format(f1, f2)
            random.shuffle(answer)

            hyperlink = '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">{}: {}</a><br>'

            #[INSERT CODE HERE. Create the 4 answer hyperlinks here using string formatting.]
            #done
            page += '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">A: {}</a><br>'.format(un,pw,f1,f2,answer[0],answer[0])
            page += '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">B: {}</a><br>'.format(un,pw,f1,f2,answer[1],answer[1])
            page += '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">C: {}</a><br>'.format(un,pw,f1,f2,answer[2],answer[2])
            page += '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">D: {}</a><br>'.format(un,pw,f1,f2,answer[3],answer[3])

            page += '''<h2>Score</h2>
            Correct: {}<br>
            Wrong: {}<br>
            <a href="/account?reset=true">Reset</a>
            </body></html>'''.format(correct, wrong)

            return [page.encode()]
        else:
            return ['Not logged in. <a href="/">Login</a>'.encode()]

    elif path == '/':
        #[INSERT CODE HERE.Create the two forms, one to login, the other to register a new account]
        page = '''
        <form action="/login" style="background-color:gold">
            <h1>Login</h1>
            Username <input type="text" name="username"><br>
            Password <input type="password" name="password"><br>
            <input type="submit" value="Log in">
        </form>
        <form action="/register" style="background-color:gold">
            <h1>Register</h1>
            Username <input type="text" name="username"><br>
            Password <input type="password" name="password"><br>
            <input type="submit" value="Register">
        </form>'''
        start_response('200 OK', headers)
        return [page.encode()]

    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]


httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()