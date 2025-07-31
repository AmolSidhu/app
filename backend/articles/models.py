from django.db import models

class MainArticle(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=False)
    content = models.TextField(null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'main_article'
        verbose_name = 'Main Article'
        verbose_name_plural = 'Main Articles'

class MassUploadFiles(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    file_location = models.CharField(max_length=300, null=False)
    file_extension = models.CharField(max_length=50, null=False, default='missing file type')
    file_status = models.CharField(max_length=50, null=False, default='uploaded')
    
    class Meta:
        db_table = 'mass_upload_files'
        verbose_name = 'Mass Upload File'
        verbose_name_plural = 'Mass Upload Files'

class ArticleTags(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    main_article = models.ForeignKey(MainArticle, on_delete=models.CASCADE, related_name='tags')
    article = models.ForeignKey(MainArticle, on_delete=models.CASCADE)
    tag = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = 'article_tags'
        verbose_name = 'Article Tag'
        verbose_name_plural = 'Article Tags'

class MyArticleList(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    my_article_list_name = models.CharField(max_length=100, null=False)
    my_article_list_description = models.CharField(max_length=300, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'my_article_list'
        verbose_name = 'My Article List'
        verbose_name_plural = 'My Article Lists'

class MyArticleListRecords(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    main_article = models.ForeignKey(MainArticle, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'my_article_list_records'
        verbose_name = 'My Article List Record'
        verbose_name_plural = 'My Article List Records'