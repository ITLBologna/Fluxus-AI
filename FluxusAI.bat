SET CURRDIR=%CD%
SET CURRDRIVE=%CD:~0,2%

C:
call "%HOMEPATH%\anaconda3\Scripts\activate.bat" mimosa

%CURRDRIVE%
cd %CURRDIR%

python entry_point.py
