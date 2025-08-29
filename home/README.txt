sudo systemctl daemon-reload
sudo systemctl reload nginx
sudo systemctl restart nginx
sudo systemctl status nginx
sudo nginx -t
python manage.py collectstatic

sudo journalctl -u gunicorn -f for error in nginx and gunicorn

