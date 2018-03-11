# distSolution
Create distribution files from Visual Studio solution

## Preparation python
* Install easywebdav  by running following command
```
easy_install easywebdav
```

## Prepare solution
1. Make sure your Solution can build entire projects by building one Project.
2. Build the solution and check distribution files are correct.
3. Run following command to create a default dist.json.
```
>python.exe ..\distSolution\createDistJson.py -sln copyuuid2013.sln c:\Linkout\copyuuid > dist.json
```
where *copyuuid2013.sln* is your solution file, *c:\Linkout\copyuuid* is a directory which contains final distribution files.

4. Edit dist.json

| name              | value                                                                                                                                                    |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| name              | name of project                                                                                                                                          |
| solution          | solution file                                                                                                                                            |
| targetproject     | project name which could build and create complete distribution files.                                                                                   |
| targets           | List of target. For example win32 and win64.                                                                                                             |
| setoutdirforbuild | if true, outdir is set as OutDir property when msbuild is launched, otherwise default OutDir ( project settings has its value) is used.                  |
| outdir            | OutDir property if needed.                                                                                                                               |
| platform          | platform                                                                                                                                                 |
| archivedir        | Directory where the archive files will be created.                                                                                                       |
| remotedir         | URL where the created archive will be uploaded by using webdav.                                                                                          |
| remotesha1        | URL to check the upload is succeeded by comparing sha1. (still in progress)                                                                              |
| TotalFileCount    | Total file count the distribution has.                                                                                                                   |
| ShouldNotBeFiles  | Files must not exist in distribution.                                                                                                                    |
| ShouldBeFiles     | Files must exist in distribution.                                                                                                                        |
| obtainverfrom     | File from which version number will be obained. Version number is used when creating an archive.                                                         |
| obtainverregex    | Version number will be obtained from the first line of "obtainverfrom" file, and this specifies Regular-expression to get version number from that line. |

(table created in https://www.tablesgenerator.com/markdown_tables# and tgn-of-md is the file saved)
