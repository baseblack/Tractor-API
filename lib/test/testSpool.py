from tractor.glue import nuke, maya, shake


def NukeSpool( arg ):
	cmd_args = { "threads":4, "fullsize":False, "quiet":True, "file":"/tmp/mynukefile.nk"}
	job_args   = { "title":"Nuke Tractor.Glue Test", "range":"1-30x2,40-53,60",  "chunksize":5, "timestamp":"jan31st", "name":"simplerender",  "user":"andrew.bunday"}

	job = nuke.Nuke( job_args, cmd_args )
	
	job.buildTaskTree()
	job.spool( arg, startpaused=True )

def MayaSpool( arg ):
	cmd_args   = { "file":"/tmp/mynukefile.ma"}
	job_args = { "title":"Maya Tractor.Glue Test" , "range":"1-30x2,40-53,60",  "chunksize":5, "timestamp":"jan31st", "name":"simplerender",  "user":"andrew.bunday", 'projectpath':'/tmp/stupid/images'}

	job = maya.MRfMaya( job_args, cmd_args )
	
	job.buildTaskTree()
	job.spool( arg, startpaused=True )
	
	
def ShakeSpool( arg ):
	cmd_args   = { "file":"/tmp/myshakefile.shk"}
	job_args = { "title":"Shake Tractor.Glue Test",  "range":"1-30x2,40-53,60",  "chunksize":5, "timestamp":"jan31st", "name":"simplerender",  "user":"andrew.bunday", 'projectpath':'/tmp/stupid/images'}

	job = shake.Shake( job_args, cmd_args )
	
	job.buildTaskTree()
	job.spool( arg )
		
def xtest_NukeSpoolStdOut( ):
	NukeSpool( 'stdout' )
	
def xtest_NukeSpoolTractor( ):
	NukeSpool( 'tractor' )
		
def xtest_MayaSpoolStdOut( ):
	MayaSpool( 'stdout' )
	
def xtest_MayaSpoolTractor( ):
	MayaSpool( 'tractor' )
	
def test_ShakeSpoolStdOut( ):
	ShakeSpool( 'stdout' )
	
def test_MayaSpoolTractor( ):
	MayaSpool( 'tractor' )