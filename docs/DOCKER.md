Run docker init
 What application platform does your project use? Python
? What version of Python do you want to use? 3.12.3
? What port do you want your app to listen on? 8000
? What is the command you use to run your app? gunicorn 'sokoni.wsgi' --bind=0.0.0.0:8000

✔ Created → .dockerignore
✔ Created → Dockerfile
✔ Created → compose.yaml
✔ Created → README.Docker.md

→ Your Docker files are ready!
  Review your Docker files and tailor them to your application.
  Consult README.Docker.md for information about using the generated files.

! Warning → Make sure your requirements.txt contains an entry for the gunicorn package, which is required to run your application.

What's next?
  Start your application by running → docker compose up --build
  Your application will be available at http://localhost:8000
