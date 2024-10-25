from django.http import HttpResponse, HttpResponseRedirect
import os
import zipfile

def download_files(work):
    # Создаем временный ZIP-файл
    zip_filename = f'files_{work.id}.zip'
    zip_filepath = os.path.join('/tmp', zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zip_file:
        for file in work.files.all():
            # Добавляем файл в ZIP
            zip_file.write(file.file.path, os.path.basename(file.file.path))

    # Отправляем ZIP-файл как ответ
    with open(zip_filepath, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response