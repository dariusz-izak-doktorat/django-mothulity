# -*- coding: utf-8 -*-

from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
import pytz
from io import BytesIO
import os
import uuid
from mothulity import views, models, forms, utils, sched


class UtilsTests(TestCase):
    """
    Tests for uploaded files validator.
    """
    def setUp(self):
        """
        Sets up class level attributes for the tests.

        Parameters
        -------
        fastq_file: str
            Path to test fastq file.
        summ_file: str
            Path to test non-fastq file.
        sinfo_raw: str
            Path to test sinfo log file.
        long_idle_nodes: int, <61>
            Number of nodes idle in queue long.
        """
        fastq_file = "mothulity/tests/Mock_S280_L001_R1_001.fastq"
        summ_file = "mothulity/tests/mothur.job.trim.contigs.summary"
        self.remote_machine = "headnode"
        self.fastq_file_remote = "/home/dizak/misc/mothulity_django_tests/Mock_S280_L001_R1_001.fastq"
        self.fastq_file = "{}/{}".format(settings.BASE_DIR,
                                         fastq_file)
        self.summ_file = "{}/{}".format(settings.BASE_DIR,
                                        summ_file)
        self.mock_md5sum = "7e4f54362bd0f030a623a6aaba27ddba"
        self.machine = "headnode"
        self.cmd = "uname"
        self.cmd_out = "Linux"
        self.sinfo_file = "mothulity/tests/sinfo.log"
        self.squeue_file = "mothulity/tests/squeue.log"
        self.long_idle_nodes = 61
        self.accel_idle_nodes = 12
        self.accel_alloc_nodes = 3
        self.JOBID_1 = 1324233
        self.JOBID_2 = 1324490
        self.PARTITION_1 = "accel"
        self.NAME_1 = "bash"
        self.USER_1 = "maciek"
        self.ST_1 = "R"
        self.TIME_1 = "13-09:03:01"
        self.NODES_1 = 1
        self.NODELIST_1 = "phi3"
        self.PARTITION_2 = "short"
        self.NAME_2 = "bash"
        self.USER_2 = "huncwot"
        self.ST_2 = "R"
        self.TIME_2 = "5:00:01"
        self.NODES_2 = 1
        self.NODELIST_2 = "n1"

    def test_sniff_true(self):
        """
        Tests whether utils.sniff returns <True> on fastq file.
        """
        self.assertIs(utils.sniff_file(self.fastq_file), True)

    def test_sniff_false(self):
        """
        Tests whether utils.sniff returns <False> on fastq file.
        """
        self.assertIs(utils.sniff_file(self.summ_file), False)

    def test_count_seqs(self):
        """
        Tests whether utils.count_seqs return expected reads number.
        """
        self.assertEqual(utils.count_seqs(self.fastq_file), 4779)

    def test_md5sum(self):
        """
        Tests whether utils.md5sum returns correct hash when run on file\
        locally.
        """
        self.assertEqual(utils.md5sum(self.fastq_file),
                         self.mock_md5sum)

    def test_md5sum_remote(self):
        """
        Tests whether utils.md5sum returns correct hash when run on file\
        rmeotely.
        """
        self.assertEqual(utils.md5sum(self.fastq_file_remote,
                                      remote=True,
                                      machine=self.remote_machine),
                         self.mock_md5sum)

    def test_parse_sinfo(self):
        """
        Tests whether sinfo log file returns expected values.
        """
        with open(self.sinfo_file) as fin:
            sinfo_str = fin.read()
        self.assertEqual(utils.parse_sinfo(sinfo_str,
                                           partition="long",
                                           state="idle"),
                         self.long_idle_nodes)
        self.assertEqual(utils.parse_sinfo(sinfo_str,
                                           partition="accel",
                                           state="idle"),
                         self.accel_idle_nodes)
        self.assertEqual(utils.parse_sinfo(sinfo_str,
                                           partition="accel",
                                           state="alloc"),
                         self.accel_alloc_nodes)

    def test_parse_squeue(self):
        """
        Test whether squeue log file returns expected values
        """
        with open(self.squeue_file) as fin:
            squeue_str = fin.read()
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_1,
                                            "JOBID"),
                         self.JOBID_1)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_1,
                                            "PARTITION"),
                         self.PARTITION_1)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_1,
                                            "NAME"),
                         self.NAME_1)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_1,
                                            "USER"),
                         self.USER_1)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_1,
                                            "ST"),
                         self.ST_1)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_1,
                                            "TIME"),
                         self.TIME_1)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_2,
                                            "JOBID"),
                         self.JOBID_2)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_2,
                                            "PARTITION"),
                         self.PARTITION_2)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_2,
                                            "NAME"),
                         self.NAME_2)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_2,
                                            "USER"),
                         self.USER_2)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_2,
                                            "ST"),
                         self.ST_2)
        self.assertEqual(utils.parse_squeue(squeue_str,
                                            self.JOBID_2,
                                            "TIME"),
                         self.TIME_2)

    def test_ssh_cmd(self):
        """
        Tests whether commands via ssh are successful.
        """
        self.assertEqual(utils.ssh_cmd(self.cmd,
                                       self.machine),
                         self.cmd_out)


class ViewsResponseTests(TestCase):
    """
    Tests for the response codes.
    """
    def setUp(self):
        """
        Sets up class level attributes for the tests.

        Parameters
        -------
        urls_list: list of str
            List urls postfixes to be tested by django's test client.
        """
        self.urls_list = ["index"]

    def test_response_code(self):
        """
        Tests whether response code of available urls equals <200>.
        """
        for url in self.urls_list:
            response = self.client.get(reverse("mothulity:{}".format(url)))
            self.assertIs(response.status_code, 200)


class ModelsTest(TestCase):
    """
    Tests for the models database API.
    """
    def setUp(self):
        """
        Sets up class level attrubutes for the tests.

        Parameters
        -------
        test_job_id: str
            UUID created ad hoc and converted into str.
        """
        self.test_job_id = str(uuid.uuid4())
        self.submission_data_dict = {"job_name": "test-job",
                                     "notify_email": "test@mail.com",
                                     "max_ambig": 0,
                                     "max_homop": 8,
                                     "min_length": 100,
                                     "max_length": 200,
                                     "min_overlap": 10,
                                     "screen_criteria": 95,
                                     "chop_length": 250,
                                     "precluster_diffs": 2,
                                     "classify_seqs_cutoff": 80,
                                     "amplicon_type": "16S"}
        self.test_seqs_count = 42
        self.test_job_status = "pending"
        self.test_submission_time = timezone.now()
        self.j_id = models.JobID(job_id=self.test_job_id)
        self.j_id.save()

    def test_job_id(self):
        """
        Tests whether job_id is properly saved and retrieved into and from the
        model.
        """
        self.assertIs(self.j_id.job_id, self.test_job_id)

    def test_seqsstats(self):
        """
        Tests whether job_id is properly saved and retrieved into and from the
        model as well as creation of seqsstats_set connected with the job_id.
        """
        stats = models.SeqsStats(job_id=self.j_id,
                                 seqs_count=self.test_seqs_count)
        stats.save()
        self.assertEqual(stats.seqs_count, self.test_seqs_count)

    def test_jobstatus(self):
        """
        Tests whether job_status and submission_time are properly saved and
        retrieved.
        """
        status = models.JobStatus(job_id=self.j_id,
                                  job_status=self.test_job_status,
                                  submission_time=self.test_submission_time)
        status.save()
        self.assertIs(status.job_status, self.test_job_status)
        self.assertIs(status.submission_time, self.test_submission_time)

    def test_submissiondata(self):
        """
        Tests whether job_name is properly sanitized - dashed replaced with
        underscores
        """
        submissiondata = models.SubmissionData(job_id=self.j_id,
                                               **self.submission_data_dict)
        submissiondata.save()
        self.assertIs(submissiondata.job_name, self.submission_data_dict["job_name"])


class FormsTest(TestCase):
    """
    Tests for the forms.
    """
    def setUp(self):
        """
        Sets up class level attrubutes for the tests.
        """
        self.form_data = {"job_name": "test-job",
                          "notify_email": "test@mail.com",
                          "max_ambig": 0,
                          "max_homop": 8,
                          "min_length": 100,
                          "max_length": 200,
                          "min_overlap": 10,
                          "screen_criteria": 95,
                          "chop_length": 250,
                          "precluster_diffs": 2,
                          "classify_seqs_cutoff": 80,
                          "amplicon_type": "16S"}
        self.clean_job_name = self.form_data["job_name"].replace("-", "_")

    def test_form_validity(self):
        form = forms.OptionsForm(self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_sanitize(self):
        form = forms.OptionsForm(self.form_data)
        if form.is_valid():
            self.assertEqual(form.cleaned_data["job_name"], self.clean_job_name)