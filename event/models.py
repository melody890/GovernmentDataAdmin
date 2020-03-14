from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# 事件来源
class EventSource(models.Model):
    name = models.CharField(max_length=100)
    aID = models.CharField(max_length=100)
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# 事件性质
class Property(models.Model):
    name = models.CharField(max_length=100)
    aID = models.CharField(max_length=100)
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# 事件类型
class Type(models.Model):
    name = models.CharField(max_length=100)
    aID = models.CharField(max_length=100)
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# 事件大类
class MainType(models.Model):
    name = models.CharField(max_length=100)
    aID = models.CharField(max_length=100)
    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        related_name='main_type',
    )
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# 事件小类
class SubType(models.Model):
    name = models.CharField(max_length=100)
    aID = models.CharField(max_length=100)
    main_type = models.ForeignKey(
        MainType,
        on_delete=models.CASCADE,
        related_name='sub_type',
    )
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# 区域
class District(models.Model):
    name = models.CharField(max_length=100)
    aID = models.CharField(max_length=100)
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# 街道
class Street(models.Model):
    name = models.CharField(max_length=100)
    aID = models.CharField(max_length=100)
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='street',
    )
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# 社区
class Community(models.Model):
    name = models.CharField(max_length=100)
    aID = models.CharField(max_length=100)
    long = models.FloatField(blank=True, default=0.0)
    lat = models.FloatField(blank=True, default=0.0)
    number = models.PositiveIntegerField(default=0)

    street = models.ForeignKey(
        Street,
        on_delete=models.CASCADE,
        related_name='community',
    )

    def __str__(self):
        return self.name


# 处置部门
class DisposeUnit(models.Model):
    name = models.CharField(max_length=100)
    aID = models.CharField(max_length=100)
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# 报告编号
class ReportNumber(models.Model):
    num = models.PositiveIntegerField(default=1)
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.num)


# 执行编号
class OperateNumber(models.Model):
    num = models.PositiveIntegerField(default=1)
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.num)


# 发生地点
class OccurPlace(models.Model):
    place = models.CharField(max_length=50, default='-')
    aID = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.place


# 执行情况
class Achieve(models.Model):
    status = models.CharField(max_length=100)
    name = models.CharField(max_length=100, blank=True)
    number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.status


class Event(models.Model):
    # 上传人员
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 问题编号
    rec_id = models.AutoField(primary_key=True)
    # 创建时间
    create_time = models.DateField(default=timezone.now)
    # 报告编号
    report_num = models.ForeignKey(
        ReportNumber,
        default=1,
        on_delete=models.CASCADE,
        related_name='event',
    )
    # 执行编号
    operate_num = models.ForeignKey(
        OperateNumber,
        default=1,
        on_delete=models.CASCADE,
        related_name='event',
    )
    # 发生地点
    occur_place = models.ForeignKey(
        OccurPlace,
        default=1,
        on_delete=models.CASCADE,
        related_name='event',
    )
    # 执行情况
    achieve = models.ForeignKey(
        Achieve,
        default=2,
        on_delete=models.CASCADE,
        related_name='event',
    )
    # 事件来源
    event_src = models.ForeignKey(
        EventSource,
        on_delete=models.CASCADE,
        related_name='event',
    )
    # 事件性质
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='event',
    )
    # 事件小类
    sub_type = models.ForeignKey(
        SubType,
        on_delete=models.CASCADE,
        related_name='event',
    )
    # 事件类型
    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        related_name='event',
        blank=True,
        default=1
    )
    # 所属社区
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='event',
    )
    # 处置部门
    dispose_unit = models.ForeignKey(
        DisposeUnit,
        on_delete=models.CASCADE,
        related_name='event',
    )

    class Meta:
        ordering = ('-create_time', )

    def __str__(self):
        return str(self.rec_id) + "    " + str(self.create_time)

