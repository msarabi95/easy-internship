FROM python:2.7.12
LABEL maintainer="Saeed"

RUN apt-get update && apt-get upgrade -y
RUN apt-get install npm -y

COPY . /
COPY easy_internship/secrets.template.py easy_internship/secrets.py

ENV VIRTUAL_ENV="$PWD/.venv"
RUN python2 -m virtualenv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# RUN python2 -m virtualenv .venv
# RUN . .venv/bin/activate
RUN curl https://files.pythonhosted.org/packages/27/79/8a850fe3496446ff0d584327ae44e7500daf6764ca1a382d2d02789accf7/pip-20.3.4-py2.py3-none-any.whl --output pip-20.3.4-py2.py3-none-any.whl
RUN python2 -m pip install pip-20.3.4-py2.py3-none-any.whl
RUN python2 -m pip install -r requirements.txt
RUN python2 manage.py migrate
RUN python2 manage.py loaddata */fixtures/*/*.json
RUN npm install -g bower
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN bower install
RUN python2 manage.py collectstatic --no-input
CMD ["python2", "manage.py", "runserver", "0.0.0.0:8080"]
