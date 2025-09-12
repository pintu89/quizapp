sudo systemctl daemon-reload
sudo systemctl reload nginx
sudo systemctl restart nginx
sudo systemctl status nginx
sudo nginx -t
python manage.py collectstatic

sudo journalctl -u gunicorn -f for error in nginx and gunicorn
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u nginx -u gunicorn -f


grep -rnw . -e "question_text"
grep -rnw . -e "option_a"
grep -rnw . -e "option_b"
grep -rnw . -e "option_c"
grep -rnw . -e "option_d"
