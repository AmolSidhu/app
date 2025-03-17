def json_imdb_video_record(title, release_year, motion_picture_rating, runtime, description,
                all_genres, rating, popularity, thumbnail_url, writers, directors,
                stars, creators, tv_series, full_release_date, main_genre, interests,
                full_image_url):
    return {
        'Title': title,
        'Release Year': release_year,
        'Full Release Date': full_release_date,
        'Motion Picture Rating': motion_picture_rating,
        'TV Series': tv_series,
        'Runtime': runtime,
        'Description': description,
        'Main Genre': main_genre,
        'Genres': all_genres,
        'Interests': interests,
        'Rating': rating,
        'Popularity': popularity,
        'Thumbnail URL': thumbnail_url,
        'Full Image URL': full_image_url,
        'Writers': writers,
        'Directors': directors,
        'Stars': stars,
        'Creators': creators
    }

def json_image_backup(image_name, image_path, image_extension, image_serial, image_description,
                      image_upload_time, tags, people, album, uploaded_by, status, user_editable,
                      originanl_image_extension, exif_data):
    return {
        'Image Name': image_name,
        'Image Path': image_path,
        'Image Extension': image_extension,
        'Image Serial': image_serial,
        'Image Description': image_description,
        'Date Uploaded': image_upload_time,
        'Original Image Extension': originanl_image_extension,
        'Tags': tags,
        'People': people,
        'Album': album,
        'Uploaded By': uploaded_by,
        'Non-User Editable': user_editable,
        'Status': status,
        'Revision History': {},
        'Exif Data': exif_data
    }
    
def json_revision_format_for_images(title=None, description=None, tags=None, people=None, status=None):
    if title is None or title == '':
        title = []
    if description is None or description == '':
        description = []
    if tags is None or tags == '':
        tags = []
    if people is None or people == '':
        people = []
    if status is None or status == '':
        status = []
    return {
        'Title': title,
        'Description': description,
        'Tags': tags,
        'People': people,
        'Status': status
    }

def json_album_backup(album_name, album_serial, album_description, album_status, album_tags, date_created):
    return {
        'Album Name': album_name,
        'Album Serial': album_serial,
        'Album Description': album_description,
        'Album Status': album_status,
        'Album Tags': album_tags,
        'Date Created': date_created,
        'Image Entries': [],
        'Image Deletions': [],
        'Revision History': {}
    }
    
def json_revision_format_for_albums(album_name=None, album_description=None,
                                    album_status=None, album_tags=None):
    if album_name is None or album_name == '':
        album_name = None,
    if album_description is None or album_description == '':
        album_description = None,
    if album_status is None or album_status == '':
        album_status = None,
    if album_tags is None or album_tags == '':
        album_tags = None,
    return {
        'Album Name': album_name,
        'Album Description': album_description,
        'Album Status': album_status,
        'Album Tags': album_tags
    }

def custom_album_backup(album_name, album_serial, album_description, album_status, album_data, date_created, creator):
    return {
        'Creator': creator,
        'Album Name': album_name,
        'Album Serial': album_serial,
        'Album Description': album_description,
        'Album Status': album_status,
        'Album Data': album_data,
        'Date Created': date_created,
        'Image Entries': [],
        'Image Deletions': [],
        'Revision History': {}
    }

def json_revision_format_for_custom_albums(album_name=None, album_description=None,
                                    album_status=None,):
    if album_name is None or album_name == '':
        album_name = None,
    if album_description is None or album_description == '':
        album_description = None,
    if album_status is None or album_status == '':
        album_status = None,
    return {
        'Album Name': album_name,
        'Album Description': album_description,
        'Album Status': album_status
    }