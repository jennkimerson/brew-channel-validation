import json
import os
import pytest
import koji
import requests
import yaml
import channel_validator as cv

# Session object for use in monkeypatching
mykoji = koji.get_profile_module("brew")
opts = vars(mykoji.config)
session = mykoji.ClientSession(mykoji.config.server, opts)


@pytest.fixture(autouse=True)
def del_session_requests(monkeypatch):
    """
    Delete rsession attr from session to avoid brew API calls
    """
    monkeypatch.delattr(session, "rsession")


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")


class FakeCall:
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        call_dirs = ["getBuildLogs", "getBuild"]
        if self.name in call_dirs:
            filename = str(args[0]) + ".json"
            fixture = os.path.join(FIXTURES_DIR, "calls", self.name, filename)
        else:
            filename = self.name + ".json"
            fixture = os.path.join(FIXTURES_DIR, "calls", filename)
        try:
            with open(fixture) as fp:
                return json.load(fp)
        except FileNotFoundError:
            print("Create new fixture file at %s" % fixture)
            print("koji call %s ... --json-output > %s" % (self.name, fixture))
            raise



# Class to mock koji session will override responses from brew API calls
class MockSession:
    def __getattr__(self, name):
        return FakeCall(name)

    # mock get_build returns test data to mock session.getBuild()
    @staticmethod
    def get_build(build_id):
        """
        returns the test build info for a given build id
        """
        build_dict = {
            "1753791": {
                "build_id": 1753791,
                "cg_id": None,
                "cg_name": None,
                "completion_time": "2021-10-07 07:45:39.428208",
                "completion_ts": 1633592739.42821,
                "creation_event_id": 41409357,
                "creation_time": "2021-10-07 07:44:02.519423",
                "creation_ts": 1633592642.51942,
                "epoch": None,
                "extra": {
                    "source": {
                        "original_url": "git://pkgs.devel.redhat.com/rpms/convert2rhel#293d829cb317d77c2a4b72dcbb9f39455e604e76"
                    }
                },
                "id": 1753791,
                "name": "convert2rhel",
                "nvr": "convert2rhel-0.24-2.el6",
                "owner_id": 3367,
                "owner_name": "mbocek",
                "package_id": 79515,
                "package_name": "convert2rhel",
                "release": "2.el6",
                "source": "git://pkgs.devel.redhat.com/rpms/convert2rhel#293d829cb317d77c2a4b72dcbb9f39455e604e76",
                "start_time": "2021-10-07 07:44:02.511531",
                "start_ts": 1633592642.51153,
                "state": 1,
                "task_id": 40191207,
                "version": "0.24",
                "volume_id": 7,
                "volume_name": "rhel-6",
            },
            "1757570": {
                "build_id": 1757570,
                "cg_id": None,
                "cg_name": None,
                "completion_time": "2021-10-11 18:33:52.018836",
                "completion_ts": 1633977232.01884,
                "creation_event_id": 41464043,
                "creation_time": "2021-10-11 18:30:42.450638",
                "creation_ts": 1633977042.45064,
                "epoch": None,
                "extra": {
                    "source": {
                        "original_url": "git://pkgs.devel.redhat.com/rpms/e2e-module-test?#0fb8c7868015e81b4ef62168cb0a71ce70f7dd2b"
                    }
                },
                "id": 1757570,
                "name": "e2e-module-test",
                "nvr": "e2e-module-test-1.0.4127-1.module+e2e+12941+acfc830c",
                "owner_id": 4066,
                "owner_name": "mbs",
                "package_id": 71581,
                "package_name": "e2e-module-test",
                "release": "1.module+e2e+12941+acfc830c",
                "source": "git://pkgs.devel.redhat.com/rpms/e2e-module-test#0fb8c7868015e81b4ef62168cb0a71ce70f7dd2b",
                "start_time": "2021-10-11 18:30:42.443708",
                "start_ts": 1633977042.44371,
                "state": 1,
                "task_id": 40263155,
                "version": "1.0.4127",
                "volume_id": 9,
                "volume_name": "rhel-8",
            },
        }
        return build_dict[build_id]

    @staticmethod
    def requests_get(url):
        """
        returns test log string for requests.get(url) for log collection
        """
        response_dict = {
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/hw_info.log": "CPU info:\nArchitecture:        aarch64\nByte Order:          Little Endian\nCPU(s):              16\nOn-line CPU(s) list: 0-15\nThread(s) per core:  1\nCore(s) per cluster: 16\nSocket(s):           -\nCluster(s):          1\nNUMA node(s):        1\nVendor ID:           Cavium\nModel:               1\nModel name:          ThunderX2 99xx\nStepping:            0x1\nBogoMIPS:            400.00\nNUMA node0 CPU(s):   0-15\nFlags:               fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics cpuid asimdrdm\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16175168     1101376    12931904       71296     2141888    12707584\nSwap:       8392640      242304     8150336\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  205G  5.9G  199G   3% /\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/hw_info.log": "CPU info:\nArchitecture:        ppc64le\nByte Order:          Little Endian\nCPU(s):              8\nOn-line CPU(s) list: 0-7\nThread(s) per core:  1\nCore(s) per socket:  8\nSocket(s):           1\nNUMA node(s):        1\nModel:               2.1 (pvr 004b 0201)\nModel name:          POWER8 (architected), altivec supported\nHypervisor vendor:   KVM\nVirtualization type: para\nL1d cache:           64K\nL1i cache:           32K\nNUMA node0 CPU(s):   0-7\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       24050560     1062144    16829376      158912     6159040    22675264\nSwap:      15744960       64000    15680960\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  198G  6.3G  192G   4% /\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/hw_info.log": "CPU info:\nArchitecture:        s390x\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Big Endian\nCPU(s):              4\nOn-line CPU(s) list: 0-3\nThread(s) per core:  1\nCore(s) per socket:  1\nSocket(s) per book:  1\nBook(s) per drawer:  1\nDrawer(s):           4\nNUMA node(s):        1\nVendor ID:           IBM/S390\nMachine type:        2964\nCPU dynamic MHz:     5000\nCPU static MHz:      5000\nBogoMIPS:            3033.00\nHypervisor:          z/VM 6.4.0\nHypervisor vendor:   IBM\nVirtualization type: full\nDispatching mode:    horizontal\nL1d cache:           128K\nL1i cache:           96K\nL2d cache:           2048K\nL2i cache:           2048K\nL3 cache:            65536K\nL4 cache:            491520K\nNUMA node0 CPU(s):   0-3\nFlags:               esan3 zarch stfle msa ldisp eimm dfp edat etf3eh highgprs te vx sie\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16284748      632200    13382456       37940     2270092    15426604\nSwap:      16777212      354700    16422512\n\n\nStorage:\nFilesystem                Size  Used Avail Use% Mounted on\n/dev/mapper/system-build  118G  2.8G  115G   3% /mnt/build\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/hw_info.log": "CPU info:\nArchitecture:        x86_64\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             3646.839\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.47\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32624292      994276    17234720      886796    14395296    30267136\nSwap:      16482300      835572    15646728\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--039-root  581G   15G  567G   3% /\n",
            "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/hw_info.log": "'CPU info:\nArchitecture:        i686\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             2261.106\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.88\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32627392      974832    10973492      961680    20679068    30210696\nSwap:      16486396      783160    15703236\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--037-root  581G   13G  569G   3% /\n",
        }
        return response_dict[url]

    @staticmethod
    def text():
        """
        overrides response.text() return. Returns hw_info.log text for
        host 94 build
        """
        return "CPU info:\nArchitecture:        ppc64le\nByte Order:          Little Endian\nCPU(s):              8\nOn-line CPU(s) list: 0-7\nThread(s) per core:  1\nCore(s) per socket:  8\nSocket(s):           1\nNUMA node(s):        1\nModel:               2.1 (pvr 004b 0201)\nModel name:          POWER8 (architected), altivec supported\nHypervisor vendor:   KVM\nVirtualization type: para\nL1d cache:           64K\nL1i cache:           32K\nNUMA node0 CPU(s):   0-7\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       24050560     1062144    16829376      158912     6159040    22675264\nSwap:      15744960       64000    15680960\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  198G  6.3G  192G   4% /\n"


def test_collect_channels():
    """
    Tests for functioning of collect_channels function
    """
    channel_list = cv.collect_channels(MockSession())

    assert len(channel_list) == 37


class FakeResponse:
            """ Class to fake response """
            def __init__(self, url):
                resp_dict = {
                    "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/hw_info.log": "CPU info:\nArchitecture:        aarch64\nByte Order:          Little Endian\nCPU(s):              16\nOn-line CPU(s) list: 0-15\nThread(s) per core:  1\nCore(s) per cluster: 16\nSocket(s):           -\nCluster(s):          1\nNUMA node(s):        1\nVendor ID:           Cavium\nModel:               1\nModel name:          ThunderX2 99xx\nStepping:            0x1\nBogoMIPS:            400.00\nNUMA node0 CPU(s):   0-15\nFlags:               fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics cpuid asimdrdm\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16175168     1101376    12931904       71296     2141888    12707584\nSwap:       8392640      242304     8150336\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  205G  5.9G  199G   3% /\n",
                    "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/hw_info.log": "CPU info:\nArchitecture:        ppc64le\nByte Order:          Little Endian\nCPU(s):              8\nOn-line CPU(s) list: 0-7\nThread(s) per core:  1\nCore(s) per socket:  8\nSocket(s):           1\nNUMA node(s):        1\nModel:               2.1 (pvr 004b 0201)\nModel name:          POWER8 (architected), altivec supported\nHypervisor vendor:   KVM\nVirtualization type: para\nL1d cache:           64K\nL1i cache:           32K\nNUMA node0 CPU(s):   0-7\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       24050560     1062144    16829376      158912     6159040    22675264\nSwap:      15744960       64000    15680960\n\n\nStorage:\nFilesystem             Size  Used Avail Use% Mounted on\n/dev/mapper/rhel-root  198G  6.3G  192G   4% /\n",
                    "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/hw_info.log": "CPU info:\nArchitecture:        s390x\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Big Endian\nCPU(s):              4\nOn-line CPU(s) list: 0-3\nThread(s) per core:  1\nCore(s) per socket:  1\nSocket(s) per book:  1\nBook(s) per drawer:  1\nDrawer(s):           4\nNUMA node(s):        1\nVendor ID:           IBM/S390\nMachine type:        2964\nCPU dynamic MHz:     5000\nCPU static MHz:      5000\nBogoMIPS:            3033.00\nHypervisor:          z/VM 6.4.0\nHypervisor vendor:   IBM\nVirtualization type: full\nDispatching mode:    horizontal\nL1d cache:           128K\nL1i cache:           96K\nL2d cache:           2048K\nL2i cache:           2048K\nL3 cache:            65536K\nL4 cache:            491520K\nNUMA node0 CPU(s):   0-3\nFlags:               esan3 zarch stfle msa ldisp eimm dfp edat etf3eh highgprs te vx sie\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       16284748      632200    13382456       37940     2270092    15426604\nSwap:      16777212      354700    16422512\n\n\nStorage:\nFilesystem                Size  Used Avail Use% Mounted on\n/dev/mapper/system-build  118G  2.8G  115G   3% /mnt/build\n",
                    "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/hw_info.log": "CPU info:\nArchitecture:        x86_64\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             3646.839\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.47\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32624292      994276    17234720      886796    14395296    30267136\nSwap:      16482300      835572    15646728\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--039-root  581G   15G  567G   3% /\n",
                    "http://download.devel.redhat.com/brewroot/vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/hw_info.log": "'CPU info:\nArchitecture:        i686\nCPU op-mode(s):      32-bit, 64-bit\nByte Order:          Little Endian\nCPU(s):              24\nOn-line CPU(s) list: 0-23\nThread(s) per core:  2\nCore(s) per socket:  6\nSocket(s):           2\nNUMA node(s):        2\nVendor ID:           GenuineIntel\nCPU family:          6\nModel:               63\nModel name:          Intel(R) Xeon(R) CPU E5-2643 v3 @ 3.40GHz\nStepping:            2\nCPU MHz:             2261.106\nCPU max MHz:         3700.0000\nCPU min MHz:         1200.0000\nBogoMIPS:            6799.88\nVirtualization:      VT-x\nL1d cache:           32K\nL1i cache:           32K\nL2 cache:            256K\nL3 cache:            20480K\nNUMA node0 CPU(s):   0,2,4,6,8,10,12,14,16,18,20,22\nNUMA node1 CPU(s):   1,3,5,7,9,11,13,15,17,19,21,23\nFlags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm ida arat pln pts md_clear flush_l1d\n\n\nMemory:\n              total        used        free      shared  buff/cache   available\nMem:       32627392      974832    10973492      961680    20679068    30210696\nSwap:      16486396      783160    15703236\n\n\nStorage:\nFilesystem                      Size  Used Avail Use% Mounted on\n/dev/mapper/rhel_x86--037-root  581G   13G  569G   3% /\n",
                }

                self.text = resp_dict[url]


@pytest.fixture
def fake_request(monkeypatch):
    """ """
    def fake_get(url):
        return FakeResponse(url)

    monkeypatch.setattr(requests, "get", fake_get)


def test_get_hw_info(test_host_with_build, fake_request, monkeypatch):
    """
    Tests for functioning of collect_hw_info function
    """
    expected = {
        "arches": ["ppc","ppc64le"],
        "CPU(s)": 8,
        "Ram": 24050560,
        "Disk": "198G",
        "Kernel": "4.18.0-193.28.1.el8_2.ppc64le",
        "Operating System": "RedHat 8.2",
    }
    my_host = test_host_with_build
    my_host.get_hw_info(MockSession())

    assert my_host.hw_dict == expected


def test_config_checker(test_channel_with_hosts):
    """
    Tests that channel.config_check and compare_hosts is working
    """
    channel = test_channel_with_hosts
    channel.config_check()

    config_items = sum([len(elem) for elem in channel.config_groups])

    assert config_items == 8 and len(channel.config_groups) == 5


@pytest.fixture
def test_channel_with_hosts():
    """
    Sets up a test channel with hosts for config checking
    """
    test_channel = cv.channel(name="dummy-rhel8", id=21)

    # set up hosts for the channel. Host data is loaded from .yml
    with open("tests/fixtures/hosts/hosts.yml", "r") as fp:
        host_yml = yaml.safe_load(fp)

        for hosts in host_yml:
            cur_yml = host_yml[hosts]
            tmp_host = cv.host(
                cur_yml["Name"],
                cur_yml["id"],
                cur_yml["enabled"],
                cur_yml["arches"],
                cur_yml["description"],
            )
            for key in tmp_host.hw_dict:
                tmp_host.hw_dict[key] = cur_yml[key]
            test_channel.host_list.append(tmp_host)

    return test_channel


@pytest.fixture
def test_host_with_build(host_94_list_host):
    """
    Sets up host to mock host 94 for testing.
    """
    test_task = cv.task(
        task_id=40263182,
        parent_id=40263155,
        build_info={
            "build_id": 1757570,
            "completion_time": "2021-10-11 18:33:52.018836",
            "completion_ts": 1633977232.01884,
            "creation_event_id": 41464043,
            "creation_time": "2021-10-11 18:30:42.450638",
            "creation_ts": 1633977042.45064,
            "epoch": None,
            "extra": {
                "source": {
                    "original_url": "git://pkgs.devel.redhat.com/rpms/e2e-module-test?#0fb8c7868015e81b4ef62168cb0a71ce70f7dd2b"
                }
            },
            "name": "e2e-module-test",
            "nvr": "e2e-module-test-1.0.4127-1.module+e2e+12941+acfc830c",
            "owner_id": 4066,
            "owner_name": "mbs",
            "package_id": 71581,
            "package_name": "e2e-module-test",
            "release": "1.module+e2e+12941+acfc830c",
            "source": "git://pkgs.devel.redhat.com/rpms/e2e-module-test#0fb8c7868015e81b4ef62168cb0a71ce70f7dd2b",
            "start_time": "2021-10-11 18:30:42.443708",
            "start_ts": 1633977042.44371,
            "state": 1,
            "task_id": 40263155,
            "version": "1.0.4127",
            "volume_id": 9,
            "volume_name": "rhel-8",
        },
    )
    test_host = cv.host(
        "rhel8", 94, True, host_94_list_host["arches"], host_94_list_host["description"]
    )
    test_host.task_list.append(test_task)
    return test_host


@pytest.fixture
def host_94_list_host():
    """
    contains the listHost dictionary for host 94
    """
    return {
        "arches": "ppc ppc64le",
        "capacity": 3.0,
        "comment": "upgrade-brew playbook",
        "description": "Updated: 2021-06-24\n"
        "Infrastructure Type: NA\n"
        "Operating System: RedHat 8.2\n"
        "Kernel: 4.18.0-193.28.1.el8_2.ppc64le\n"
        "vCPU Count: 8\n"
        "Total Memory: 23.497 gb\n",
        "enabled": True,
        "id": 94,
        "name": "ppc-016.build.eng.bos.redhat.com",
        "ready": True,
        "task_load": 0.4,
        "user_id": 1744,
    }


@pytest.fixture
def mock_get_build_dict():
    """
    Returns a dictionary of buildID: build info for the mock_get_build function
    """
    build_dict = {
        "1753791": {
            "build_id": 1753791,
            "cg_id": None,
            "cg_name": None,
            "completion_time": "2021-10-07 07:45:39.428208",
            "completion_ts": 1633592739.42821,
            "creation_event_id": 41409357,
            "creation_time": "2021-10-07 07:44:02.519423",
            "creation_ts": 1633592642.51942,
            "epoch": None,
            "extra": {
                "source": {
                    "original_url": "git://pkgs.devel.redhat.com/rpms/convert2rhel#293d829cb317d77c2a4b72dcbb9f39455e604e76"
                }
            },
            "id": 1753791,
            "name": "convert2rhel",
            "nvr": "convert2rhel-0.24-2.el6",
            "owner_id": 3367,
            "owner_name": "mbocek",
            "package_id": 79515,
            "package_name": "convert2rhel",
            "release": "2.el6",
            "source": "git://pkgs.devel.redhat.com/rpms/convert2rhel#293d829cb317d77c2a4b72dcbb9f39455e604e76",
            "start_time": "2021-10-07 07:44:02.511531",
            "start_ts": 1633592642.51153,
            "state": 1,
            "task_id": 40191207,
            "version": "0.24",
            "volume_id": 7,
            "volume_name": "rhel-6",
        },
        "1757570": {
            "build_id": 1757570,
            "cg_id": None,
            "cg_name": None,
            "completion_time": "2021-10-11 18:33:52.018836",
            "completion_ts": 1633977232.01884,
            "creation_event_id": 41464043,
            "creation_time": "2021-10-11 18:30:42.450638",
            "creation_ts": 1633977042.45064,
            "epoch": None,
            "extra": {
                "source": {
                    "original_url": "git://pkgs.devel.redhat.com/rpms/e2e-module-test?#0fb8c7868015e81b4ef62168cb0a71ce70f7dd2b"
                }
            },
            "id": 1757570,
            "name": "e2e-module-test",
            "nvr": "e2e-module-test-1.0.4127-1.module+e2e+12941+acfc830c",
            "owner_id": 4066,
            "owner_name": "mbs",
            "package_id": 71581,
            "package_name": "e2e-module-test",
            "release": "1.module+e2e+12941+acfc830c",
            "source": "git://pkgs.devel.redhat.com/rpms/e2e-module-test#0fb8c7868015e81b4ef62168cb0a71ce70f7dd2b",
            "start_time": "2021-10-11 18:30:42.443708",
            "start_ts": 1633977042.44371,
            "state": 1,
            "task_id": 40263155,
            "version": "1.0.4127",
            "volume_id": 9,
            "volume_name": "rhel-8",
        },
    }
    return build_dict


@pytest.fixture
def mock_get_build_logs_dict():
    """
    returns a dict of {buildID : [build logs]} for the mock_get_build_logs function
    """
    log_dict = {
        "1753791": [
            {
                "dir": "noarch",
                "name": "state.log",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/state.log",
            },
            {
                "dir": "noarch",
                "name": "build.log",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/build.log",
            },
            {
                "dir": "noarch",
                "name": "root.log",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/root.log",
            },
            {
                "dir": "noarch",
                "name": "mock_output.log",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/mock_output.log",
            },
            {
                "dir": "noarch",
                "name": "noarch_rpmdiff.json",
                "path": "vol/rhel-6/packages/convert2rhel/0.24/2.el6/data/logs/noarch/noarch_rpmdiff.json",
            },
        ],
        "1757570": [
            {
                "dir": "aarch64",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/hw_info.log",
            },
            {
                "dir": "aarch64",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/state.log",
            },
            {
                "dir": "aarch64",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/build.log",
            },
            {
                "dir": "aarch64",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/root.log",
            },
            {
                "dir": "aarch64",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/installed_pkgs.log",
            },
            {
                "dir": "aarch64",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/aarch64/mock_output.log",
            },
            {
                "dir": "i686",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/hw_info.log",
            },
            {
                "dir": "i686",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/state.log",
            },
            {
                "dir": "i686",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/build.log",
            },
            {
                "dir": "i686",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/root.log",
            },
            {
                "dir": "i686",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/installed_pkgs.log",
            },
            {
                "dir": "i686",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/i686/mock_output.log",
            },
            {
                "dir": "ppc64le",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/hw_info.log",
            },
            {
                "dir": "ppc64le",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/state.log",
            },
            {
                "dir": "ppc64le",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/build.log",
            },
            {
                "dir": "ppc64le",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/root.log",
            },
            {
                "dir": "ppc64le",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/installed_pkgs.log",
            },
            {
                "dir": "ppc64le",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/ppc64le/mock_output.log",
            },
            {
                "dir": "s390x",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/hw_info.log",
            },
            {
                "dir": "s390x",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/state.log",
            },
            {
                "dir": "s390x",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/build.log",
            },
            {
                "dir": "s390x",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/root.log",
            },
            {
                "dir": "s390x",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/installed_pkgs.log",
            },
            {
                "dir": "s390x",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/s390x/mock_output.log",
            },
            {
                "dir": "x86_64",
                "name": "hw_info.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/hw_info.log",
            },
            {
                "dir": "x86_64",
                "name": "state.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/state.log",
            },
            {
                "dir": "x86_64",
                "name": "build.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/build.log",
            },
            {
                "dir": "x86_64",
                "name": "root.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/root.log",
            },
            {
                "dir": "x86_64",
                "name": "installed_pkgs.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/installed_pkgs.log",
            },
            {
                "dir": "x86_64",
                "name": "mock_output.log",
                "path": "vol/rhel-8/packages/e2e-module-test/1.0.4127/1.module+e2e+12941+acfc830c/data/logs/x86_64/mock_output.log",
            },
        ],
    }
    return log_dict


@pytest.fixture
def test_list_task_data():
    return [
        {
            "arch": "i386",
            "awaited": False,
            "channel_id": 26,
            "completion_time": "2021-06-15 11:05:53.245114",
            "completion_ts": 1623755153.24511,
            "create_time": "2021-06-15 11:03:15.121289",
            "create_ts": 1623754995.12129,
            "host_id": 280,
            "id": 37493015,
            "label": "i686",
            "method": "buildArch",
            "owner": 4132,
            "owner_name": "crecklin",
            "owner_type": 0,
            "parent": 37492841,
            "priority": 19,
            "request": [
                "tasks/2847/37492847/kernel-3.10.0-1160.32.1.el7.1964556.test.cki.src.rpm",
                67194,
                "i686",
                False,
                {"repo_id": 5081187},
            ],
            "result": [
                {
                    "brootid": 7490808,
                    "logs": [
                        "tasks/3015/37493015/build.log",
                        "tasks/3015/37493015/root.log",
                        "tasks/3015/37493015/state.log",
                        "tasks/3015/37493015/mock_output.log",
                    ],
                    "rpms": [
                        "tasks/3015/37493015/kernel-headers-3.10.0-1160.32.1.el7.1964556.test.cki.i686.rpm"
                    ],
                    "srpms": [],
                }
            ],
            "start_time": "2021-06-15 11:04:02.183543",
            "start_ts": 1623755042.18354,
            "state": 2,
            "waiting": None,
            "weight": 2.5,
        }
    ]