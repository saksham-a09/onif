from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0001_initial'),
    ]

    operations = [
        # Add deposit proof fields
        migrations.AddField(
            model_name='investment',
            name='deposit_network',
            field=models.CharField(
                blank=True,
                choices=[('BEP20', 'BEP20 (BSC)'), ('TRC20', 'TRC20 (TRON)')],
                max_length=10,
                verbose_name='Deposit Network',
            ),
        ),
        migrations.AddField(
            model_name='investment',
            name='deposit_txn_hash',
            field=models.CharField(
                blank=True, db_index=True, max_length=200,
                verbose_name='Deposit Transaction Hash',
            ),
        ),
        migrations.AddField(
            model_name='investment',
            name='deposit_sender_address',
            field=models.CharField(
                blank=True, max_length=200,
                verbose_name='Sender Wallet Address',
            ),
        ),
        migrations.AddField(
            model_name='investment',
            name='deposit_proof',
            field=models.FileField(
                blank=True, null=True,
                upload_to='investment_deposits/',
                verbose_name='Deposit Proof Screenshot',
            ),
        ),
        migrations.AddField(
            model_name='investment',
            name='deposit_submitted_at',
            field=models.DateTimeField(
                blank=True, null=True,
                verbose_name='Deposit Submitted At',
            ),
        ),
        # Update status choices and default to DEPOSIT_PENDING
        migrations.AlterField(
            model_name='investment',
            name='status',
            field=models.CharField(
                choices=[
                    ('DEPOSIT_PENDING', 'Deposit Pending'),
                    ('PENDING', 'Pending'),
                    ('ACTIVE', 'Active'),
                    ('COMPLETED', 'Completed'),
                    ('REJECTED', 'Rejected'),
                    ('CANCELLED', 'Cancelled'),
                ],
                db_index=True,
                default='DEPOSIT_PENDING',
                max_length=20,
                verbose_name='Status',
            ),
        ),
        # Add index for oldest-active-plan queries
        migrations.AddIndex(
            model_name='investment',
            index=models.Index(fields=['user', 'start_date'], name='investments_user_start_date_idx'),
        ),
    ]
