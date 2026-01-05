FROM odoo:18.0

# نسخ الإضافات الخاصة بك إلى المجلد المخصص داخل الحاوية
COPY ./custom_addons /mnt/extra-addons

# (اختياري) إذا كان لديك مكتبات بايثون إضافية
# COPY ./requirements.txt /
# RUN pip install -r /requirements.txt

USER odoo