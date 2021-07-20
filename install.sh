
export PROJECT_NAME='simpletrader'

useradd --no-create-home -s /usr/sbin/nologin $PROJECT_NAME
mkdir /var/log/$PROJECT_NAME
chown -R $PROJECT_NAME:$PROJECT_NAME /var/log/$PROJECT_NAME

mkdir /etc/$PROJECT_NAME
cp *.json /etc/$PROJECT_NAME
chown -R $PROJECT_NAME:$PROJECT_NAME /etc/$PROJECT_NAME

cp configs/nginx.conf /etc/nginx/sites-available/$PROJECT_NAME.conf
ln -s /etc/nginx/sites-available/$PROJECT_NAME.conf /etc/nginx/sites-enabled/$PROJECT_NAME.conf

for filename in configs/*.txt; do
    for ((i=0; i<=3; i++)); do
        ./MyProgram.exe "$filename" "Logs/$(basename "$filename" .txt)_Log$i.txt"
    done
done