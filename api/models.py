# Create your models here.

from django.db import models


# Create your models here.

class AddressInfo(models.Model):
    id = models.BigIntegerField(verbose_name="统计用区划代码", primary_key=True)
    code = models.BigIntegerField(null=True, blank=True, verbose_name="城乡分类代码")
    name = models.CharField(max_length=20, verbose_name='名称')
    ddd = models.IntegerField(null=True, blank=True, verbose_name="长途区号")
    post_code = models.IntegerField(null=True, blank=True, verbose_name="邮政编码")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PoemsAuthors(models.Model):
    """"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, null=False)  # 名字
    intro_l = models.TextField(null=False)
    intro_s = models.TextField(null=False)
    dynasty = models.CharField(max_length=15, null=True, default="null", help_text=" S-宋朝， T-唐朝")

    class Meta:
        db_table = "tb_poems_author"
        verbose_name = "poems_author"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PoetryAuthors(models.Model):
    """ """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, null=False)  # 名字
    intro = models.TextField(null=False)
    dynasty = models.CharField(max_length=15, null=True, default="null", help_text=" S-宋朝， T-唐朝")

    class Meta:
        db_table = "tb_poetry_author"
        verbose_name = "poetry_author"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ChinesePoems(models.Model):
    """

    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, null=False)  # 名字
    content = models.TextField(null=False)
    author_id = models.IntegerField(verbose_name="作者ID")
    dynasty = models.CharField(max_length=15, null=True, default="null", help_text="诗词所属年代， S-宋朝， T-唐朝")
    author = models.CharField(max_length=150, verbose_name='作者')

    class Meta:
        db_table = "tb_poems"
        verbose_name = "poems"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ChinesePoetry(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, null=False)  # 名字
    yunlv_rule = models.TextField(null=False)
    # author_id = models.IntegerField(null=False)
    # author_id = models.ForeignKey(PoetryAuthors, on_delete=models.CASCADE, verbose_name="作者")
    author_id = models.IntegerField(verbose_name="作者ID")

    content = models.TextField(null=False)
    dynasty = models.CharField(max_length=20, null=True, default="null", help_text="诗词所属年代， S-宋朝， T-唐朝")
    # author = models.CharField(max_length=20, null=False, default="null")
    author = models.CharField(max_length=150, verbose_name='作者')

    class Meta:
        db_table = "tb_poetry"
        verbose_name = "poetry"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class RelationPoems(models.Model):
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(PoemsAuthors, on_delete=models.CASCADE, verbose_name="作者")
    poems = models.ForeignKey("self", on_delete=models.CASCADE, verbose_name="作品")

    class Meta:
        db_table = "tb_peoms_relation"
        verbose_name = "peoms_relation"
        verbose_name_plural = verbose_name


class UniversityDepartment(models.Model):
    id = models.IntegerField(auto_created=True)
    sid = models.IntegerField(null=False, verbose_name="school_id")
    did = models.IntegerField(null=False, verbose_name="department_id")
    name = models.CharField(max_length=255, primary_key=True)

    class Meta:
        db_table = "department"
        verbose_name = "院系"
        verbose_name_plural = verbose_name


class ChineseUniversity(models.Model):
    id = models.IntegerField(null=False, auto_created=True)
    sid = models.IntegerField(null=False, verbose_name="school_id")
    cid = models.IntegerField(null=False, verbose_name="city_id")
    name = models.CharField(max_length=255, primary_key=True)

    class Meta:
        db_table = "school"
        verbose_name = "学校"
        verbose_name_plural = verbose_name
