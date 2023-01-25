FROM analysis_base_image


WORKDIR /app

COPY . .
RUN pip install -r requirements.txt
RUN chmod +x ./entrypoint.*.sh
