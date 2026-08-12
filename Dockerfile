FROM python:2.7.12
LABEL maintainer="Saeed"

RUN echo "deb http://archive.debian.org/debian jessie main" > /etc/apt/sources.list \
    && echo "deb http://archive.debian.org/debian-security jessie/updates main" >> /etc/apt/sources.list \
    && apt-get -o Acquire::Check-Valid-Until=false update \
    && apt-get install -y --no-install-recommends npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

COPY easy_internship/secrets.template.py easy_internship/secrets.py

ENV VIRTUAL_ENV=/app/.venv
RUN python2 -m virtualenv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN curl -L \
    https://files.pythonhosted.org/packages/27/79/8a850fe3496446ff0d584327ae44e7500daf6764ca1a382d2d02789accf7/pip-20.3.4-py2.py3-none-any.whl \
    --output /tmp/pip-20.3.4-py2.py3-none-any.whl \
    && python2 -m pip install /tmp/pip-20.3.4-py2.py3-none-any.whl \
    && rm /tmp/pip-20.3.4-py2.py3-none-any.whl

RUN python2 -m pip install -r requirements.txt

RUN python2 manage.py migrate
RUN python2 manage.py loaddata */fixtures/*/*.json

RUN npm install -g bower

RUN ln -s /usr/bin/nodejs /usr/bin/node

RUN bower install --allow-root

RUN python2 manage.py collectstatic --no-input

CMD ["python2", "manage.py", "runserver", "0.0.0.0:8080"]
