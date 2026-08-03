# apps/image_editor/migrations/0002_enhanced_image_models.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('image_editor', '0001_initial'),
    ]

    operations = [
        # Add new fields to ImageProject (keep image field for backward compatibility)
        migrations.AddField(
            model_name='imageproject',
            name='base_image',
            field=models.ImageField(blank=True, null=True, upload_to='image_editor/base/'),
        ),
        migrations.AddField(
            model_name='imageproject',
            name='canvas_data',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='imageproject',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='imageproject',
            name='height',
            field=models.IntegerField(default=600),
        ),
        migrations.AddField(
            model_name='imageproject',
            name='layer_order',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='imageproject',
            name='layers',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='imageproject',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='image_editor/thumbnails/'),
        ),
        migrations.AddField(
            model_name='imageproject',
            name='width',
            field=models.IntegerField(default=800),
        ),
        migrations.AddIndex(
            model_name='imageproject',
            index=models.Index(fields=['owner', '-updated_at'], name='image_editor_owner_idx'),
        ),
        migrations.AlterModelOptions(
            name='imageproject',
            options={'ordering': ['-updated_at']},
        ),
        # Create new models
        migrations.CreateModel(
            name='ImageLayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Layer', max_length=100)),
                ('layer_type', models.CharField(
                    choices=[('canvas', 'Canvas Layer'), ('text', 'Text Layer'), ('shape', 'Shape Layer'), ('image', 'Image Layer')],
                    default='canvas',
                    max_length=20
                )),
                ('data', models.JSONField(blank=True, default=dict)),
                ('opacity', models.FloatField(default=1.0)),
                ('blend_mode', models.CharField(
                    choices=[
                        ('normal', 'Normal'),
                        ('multiply', 'Multiply'),
                        ('screen', 'Screen'),
                        ('overlay', 'Overlay'),
                        ('soft-light', 'Soft Light'),
                        ('hard-light', 'Hard Light'),
                        ('color-dodge', 'Color Dodge'),
                        ('color-burn', 'Color Burn'),
                        ('darken', 'Darken'),
                        ('lighten', 'Lighten'),
                    ],
                    default='normal',
                    max_length=20
                )),
                ('visible', models.BooleanField(default=True)),
                ('locked', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='layer_objects', to='image_editor.imageproject')),
            ],
            options={
                'ordering': ['-order'],
            },
        ),
        migrations.CreateModel(
            name='TextLayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('font_family', models.CharField(default='Arial', max_length=100)),
                ('font_size', models.IntegerField(default=24)),
                ('font_weight', models.CharField(default='normal', max_length=20)),
                ('color', models.CharField(default='#000000', max_length=7)),
                ('x', models.IntegerField(default=0)),
                ('y', models.IntegerField(default=0)),
                ('layer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='text_data', to='image_editor.imagelayer')),
            ],
        ),
        migrations.AddConstraint(
            model_name='imagelayer',
            constraint=models.UniqueConstraint(fields=['project', 'name'], name='unique_layer_name_per_project'),
        ),
    ]
