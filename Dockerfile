FROM python
 
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/social_network

COPY Pipfile Pipfile.lock /usr/src/social_network/
RUN pip install pipenv && pipenv install --system


COPY . /usr/src/social_network/
