from django.db import models

def uploadAchievementsPath(instance, filename):
    return '%s/Achievements/%s' % (instance.user.username, filename)

class Achievements(models.Model):
    POINTS = (
        ('I', 1),
        ('V', 5),
        ('X', 10),
        ('L', 50),
        ('C', 100),
        ('D', 500),
        ('M', 1000),
    )
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=145)
    points = models.IntegerField(default=0, choices=POINTS)
    image = models.ImageField(upload_to=uploadAchievementsPath, verbose_name='image', blank=True, null=True)
    
    def __str__(self):
        return '%s %s' % (self.name, self.description)
    
    def setName(self, name):
        self.name = name
    
    def setDescription(self, description):
        self.description = description
        
    
    def setPoints(self, points):
        self.points = points
        
    
