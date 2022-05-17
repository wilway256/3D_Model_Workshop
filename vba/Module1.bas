Attribute VB_Name = "Model"
Option Explicit

Function Worksheet_Exists(sheetName As String) As Boolean
Worksheet_Exists = False
Dim i As Integer
  With ThisWorkbook
    For i = 1 To .Sheets.Count
        If .Sheets(i).name = sheetName Then
            Worksheet_Exists = True
            Exit Function
        End If
    Next i
  End With
End Function

Sub Make_New_Sheet(sheetName As String, ParamArray colNames() As Variant)
  Application.DisplayAlerts = False
  'If sheet does not already exist
  If Worksheet_Exists(sheetName) Then
    Sheets(sheetName).Delete
    'To disable warning message, Application.DisplayAlerts = False
  End If
  'Make new sheet
  Worksheets.Add(After:=Sheets(Sheets.Count)).name = sheetName
  Application.DisplayAlerts = True
  'Columns
  Dim i As Integer
  For i = 0 To UBound(colNames())
    Worksheets(sheetName).Cells(1, i + 1).Value = colNames(i)
  Next i
  i = i + 1
  With Sheets(sheetName)
  .Columns(i).Resize(.Rows.Count, .Columns.Count - i + 1).Select
  Selection.EntireColumn.Hidden = True
  End With
End Sub

Function Next_Row(sheetName As String) As Long
'Will retrieve row number of next empty row at end of table. Will ignore empty rows in a table.
  Dim sh As Worksheet
  Set sh = Sheets(sheetName)
  Next_Row = sh.Range("A" & Rows.Count).End(xlUp).Offset(1).row
End Function

Function Next_Empty_Row(sheetName As String) As Long
'Will retrieve row number of next empty row. Will find empty rows in a table.
  Dim sh As Worksheet
  Set sh = Sheets(sheetName)
  Next_Empty_Row = sh.Range("A1").End(xlDown).row
  
  'If there is no rows other than the header
  If Next_Empty_Row = sh.Rows.Count Then
    Next_Empty_Row = 2
    
  'Else: normally
  Else
    Next_Empty_Row = Next_Empty_Row + 1
  End If
  
End Function

Sub Set_Tag(rng As Range)
  Dim tag As Long
  tag = Application.Aggregate(4, 2, rng.EntireColumn) + 1 'Max of column, ignore errors
  rng.Value = tag
End Sub

Sub Add_Group_Tag(rng As Range, tag As String)
'Sets cell value if blank. Appends value with delimiter if not.
'Ending semicolon needed for Python parsing
  If tag = "" Then
    'Do nothing
  
  ElseIf rng.Value = "" Then
    rng.Value = tag & ";"
    
  Else
    rng.Value = rng.Value & " " & tag & ";"
  End If
End Sub

Sub Add_Node(name As String, x As String, y As String, z As String, ParamArray groupTags() As Variant)
  'Get next empty row
  Dim nextRow As Long
  nextRow = Next_Row("nodes")
  
  With Sheets("nodes")
    'Name Node
    .Cells(nextRow, 1).Value = name
    'Set tag
    Call Set_Tag(.Cells(nextRow, 2))
    'X, Y, and Z
    .Cells(nextRow, 3).Formula = x
    .Cells(nextRow, 3).Value = .Cells(nextRow, 3).Value
    .Cells(nextRow, 4).Formula = y
    .Cells(nextRow, 4).Value = .Cells(nextRow, 4).Value
    .Cells(nextRow, 5).Formula = z
    .Cells(nextRow, 5).Value = .Cells(nextRow, 5).Value
    'Add group tags, if applicable.
    Dim i As Integer
    For i = 0 To UBound(groupTags())
      Call Add_Group_Tag(.Cells(nextRow, 6), CStr(groupTags(i)))
    Next i
  End With
End Sub

Sub Add_Fixed_Node(name As String, fixity As String)
  Dim nextRow As Long
  nextRow = Next_Row("nodeFix")
  'Add node to list of fixed nodes.
  Sheets("nodeFix").Cells(nextRow, 1).Value = name
  'Copy 6 DOF Fixed/Free to nodeFix sheet depending on fixity type.
  Dim i As Double
  i = Application.WorksheetFunction.Match(fixity, Range("Fixity").Columns(1), 0)
  Dim sourceRange As Range
  Set sourceRange = Range(Range("Fixity").Cells(1, 2), Range("Fixity").Cells(Range("Fixity").Rows.Count, 7))
  sourceRange.Rows(i).Copy _
    Destination:=Sheets("nodeFix").Cells(nextRow, 2)
End Sub

Sub Add_Diaphragm_Constraint(constrainedNode As String, retainedNode As String)
  Dim nextRow As Long
  nextRow = Next_Row("diaphragms")
  'Add nodes to diaphragm sheet.
  With Sheets("diaphragms")
    .Cells(nextRow, 1).Value = constrainedNode
    .Cells(nextRow, 2).Value = retainedNode
  End With
End Sub

Sub Add_Nodal_Mass(nodeName As String, latMass As Double, rotMass As Double)
  Dim nextRow As Long
  nextRow = Next_Row("nodeMass")
  'Add nodes to diaphragm sheet.
  With Sheets("nodeMass")
    .Cells(nextRow, 1).Value = nodeName
    .Cells(nextRow, 2).Value = latMass
    .Cells(nextRow, 3).Value = latMass
    .Cells(nextRow, 7).Value = rotMass
    .Range("D" & nextRow & ":F" & nextRow).Value = 0
  End With
End Sub

Sub Add_Element(eleName As String, eleType As String, iNode As String, jNode As String, property As String, transformation As String, ParamArray groupTags() As Variant)
  'eleType refers to the OpenSees element command's first argument. William's cod
  'property referst to another sheet with element properties (A, I, E, etc.)
  Dim nextRow As Long
  nextRow = Next_Empty_Row("elements")
  With Sheets("elements")
    .Cells(nextRow, 1).Value = eleName
    Call Set_Tag(.Cells(nextRow, 2))
    .Cells(nextRow, 3).Value = eleType
    .Cells(nextRow, 4).Value = iNode
    .Cells(nextRow, 5).Value = jNode
    .Cells(nextRow, 6).Value = property
    .Cells(nextRow, 7).Value = transformation
    
    'Add group tags, if applicable.
    Dim i As Integer
    For i = 0 To UBound(groupTags())
      Call Add_Group_Tag(.Cells(nextRow, 8), CStr(groupTags(i)))
    Next i
  End With
End Sub

Sub Floors_and_Columns()
  
  'Create new sheets
  Call Make_New_Sheet("nodes", "NodeUID", "Tag", "X", "Y", "Z", "Group")
  Call Make_New_Sheet("nodeFix", "NodeID", "X", "Y", "Z", "MX", "MY", "MZ")
  Call Make_New_Sheet("diaphragms", "ConstrainedNode", "RetainedNode")
  Call Make_New_Sheet("nodeMass", "NodeUID", "X", "Y", "Z", "MX", "MY", "MZ")
  
  Call Make_New_Sheet("elements", "Element", "Tag", "Type", "iNode", "jNode", "PropertyID", "Transformation", "Group")
  
  'Loop through all floors
  Dim rng As Range
  Dim N As Long
  Dim floorName As String
  Dim lastFloorName As String
  N = FloorPlan.Range("Floor_Plan_Center_Table").Rows.Count
  Dim iFloor As Integer
  Dim target As Worksheet
  Set target = Sheets("nodes")
  Dim nodeName As String
  Dim centerNodeName As String
  For iFloor = 1 To N Step 1
    floorName = Range("Floor_Plan_Center_Table").Cells(iFloor, 1).Value
    centerNodeName = floorName & "_center"
    'First, add diaphragm nodes to each floor except the first
    If iFloor <> 1 Then
      Call Add_Node(centerNodeName, _
        Range("Floor_Plan_Center_Table").Cells(iFloor, 3).Value, _
        Range("Floor_Plan_Center_Table").Cells(iFloor, 4).Value, _
        "=VLOOKUP(VLOOKUP(""" & floorName & """,Floor_Plan_Center_Table,2,FALSE),Grid,2,FALSE)", _
        "floor mass")
      Call Add_Fixed_Node(centerNodeName, "Diaphragm")
      Call Add_Nodal_Mass(centerNodeName, _
        Range("Floor_Plan_Center_Table").Cells(iFloor, 5), _
        Range("Floor_Plan_Center_Table").Cells(iFloor, 6))
    End If
    
    'Second: Add every node on floor to the list of nodes.
    Dim row As Range
    For Each row In Range("Floor_Plan_Node_Table").Rows
      'Create node. Pass over nodes that do not exist on ground floor.
      nodeName = floorName & row.Cells(1).Value
      If iFloor <> 1 Or row.Cells(5).Value <> "None" Then
        Call Add_Node( _
          floorName & row.Cells(1).Value, _
          "=VLOOKUP(""" & row.Cells(2).Value & """,Grid,2,FALSE)", _
          "=VLOOKUP(""" & row.Cells(3).Value & """,Grid,2,FALSE)", _
          "=VLOOKUP(VLOOKUP(""" & floorName & """,Floor_Plan_Center_Table,2,FALSE),Grid,2,FALSE)", _
          floorName, row.Cells(1, 6).Value)
      End If
      
      'Create supports on ground floor
      If iFloor = 1 And row.Cells(1, 5).Value <> "None" Then
        Call Add_Fixed_Node(nodeName, fixity:=row.Cells(1, 5).Value)
        'Add "support" to node group
        Call Add_Group_Tag(Sheets("nodes").Cells(Next_Row("nodes") - 1, 6), "base support")
        
      'Add nodes to diaphragm constraints.
      ElseIf iFloor <> 1 And row.Cells(4) Then
        Call Add_Diaphragm_Constraint(nodeName, centerNodeName)
      End If
      
    Next row
    
    'Third: Add every floor element to the list of elements
    If iFloor <> 1 Then
      For Each row In Range("Floor_Plan_Elements_Horiz").Rows
        Call Add_Element(floorName & row.Cells(1), _
          row.Cells(2), _
          floorName & row.Cells(3), _
          floorName & row.Cells(4), _
          row.Cells(5), _
          row.Cells(6))
      Next row
    'Fourth: Add interstory elements (columns and walls)
    
      For Each row In Range("Floor_Plan_Elements_Vert").Rows
        Call Add_Element(floorName & row.Cells(1), _
          row.Cells(2), _
          lastFloorName & row.Cells(3), _
          floorName & row.Cells(3), _
          row.Cells(4), _
          row.Cells(5))
      Next row
    End If
    lastFloorName = floorName
  Next iFloor
  
  'Formatting Tidbits
  Sheets("nodes").Columns(6).AutoFit
  Sheets("diaphragms").Range("A:B").ColumnWidth = 20
  Sheets("elements").Columns("A").AutoFit
  Sheets("elements").Columns("C").ColumnWidth = 18.5
  Sheets("elements").Columns("F:G").ColumnWidth = 13.8
  Sheets("elements").Columns("H").AutoFit
End Sub

Sub Get_Grid_Coord(name As String)
  
End Sub

Sub Discretize_Element(name As String, N As Integer)
'Split element into N equal length pieces. Add applicable nodes.
  'Error Checking
  If N <= 1 Then
    MsgBox "Must discretize into at least two elements"
    Exit Sub
  End If
  'Declare ranges
  Dim eleTable As Range
  Set eleTable = Sheets("elements").Range("A2", "H" & Cells(Rows.Count, 1).End(xlUp).row)
  
  'Find existing element to discretize
  Dim iRow As Long
  iRow = WorksheetFunction.Match(name, eleTable.Columns(1), 0)
  Dim iNode As String, jNode As String, eleName As String, eleType As String, eleProperty As String, eleTransform As String, eleGroup As String
  eleName = eleTable.Cells(iRow, 1).Value
  eleType = eleTable.Cells(iRow, 3).Value
  iNode = eleTable.Cells(iRow, 4).Value
  jNode = eleTable.Cells(iRow, 5).Value
  eleProperty = eleTable.Cells(iRow, 6).Value
  eleTransform = eleTable.Cells(iRow, 7).Value
  eleGroup = eleTable.Cells(iRow, 8).Value
  If eleGroup <> "" Then
    eleGroup = Left(eleGroup, Len(eleGroup) - 1)
  End If
  
  'Get endpoint coordinates
  Dim ix As Double, iy As Double, iz As Double, jx As Double, jy As Double, jz As Double
  ix = Get_Table_Property("nodes", iNode, "X")
  iy = Get_Table_Property("nodes", iNode, "Y")
  iz = Get_Table_Property("nodes", iNode, "Z")
  jx = Get_Table_Property("nodes", jNode, "X")
  jy = Get_Table_Property("nodes", jNode, "Y")
  jz = Get_Table_Property("nodes", jNode, "Z")
  
  Dim nodeGroup As String
  If nodeGroup <> "" Then
    nodeGroup = Left(nodeGroup, Len(nodeGroup) - 1)
    nodeGroup = Trim(Replace(nodeGroup, "main;", "")) 'Remove "main" tag
  End If
  
  'Add nodes
  Dim i As Integer
  For i = 1 To N - 1
    Call Add_Node(eleName & "-" & i, _
                  ix + i * (jx - ix) / N, _
                  ix + i * (jx - ix) / N, _
                  ix + i * (jx - ix) / N, _
                  nodeGroup, "discr")
  Next i
  
  'Change first element name and jNode
  
  eleTable.Cells(iRow, 1).Value = eleTable.Cells(iRow, 1).Value & "-1"
  eleTable.Cells(iRow, 5).Value = eleName & "-1"
  'All other additional elements if N > 2
  eleTable.Range("A" & iRow).EntireRow.Offset(1).Resize(N - 1).Insert
  Dim newName As String
  For i = 2 To N
    newName = eleName & "-" & i
    If i = N Then 'If last element jNode changes
      Call Add_Element(newName, eleType, eleName & "-" & (i - 1), jNode, eleProperty, eleTransform, eleGroup)
    Else
      Call Add_Element(newName, eleType, eleName & "-" & (i - 1), eleName & "-" & i, eleProperty, eleTransform, eleGroup)
    End If
  Next i
  'Change last element name and iNode
  
End Sub

Sub Cut_Element(eleName As String, x As Double, append As String)
  Dim newName As String
  newName = eleName & "_" & append
  'Get information about original element
  'Dim eleType As String, iNode As String, jNode As String, property As String, transformation As String, group As String
  
  'Add node along element at x
  'Change eleName jNode
  'Add new element
  'Call Add_Element(newName, eleType, iNode, jNode, property, transformation)
  'Call Add_Group_Tag
End Sub

Function Get_Table_Property(sh As String, UID As String, colStr As String) As String
'Written 04-Apr-2022
'Works similar to VLOOKUP for a sheet with one data table
  Dim rng As Range
  Set rng = Table_Range(sh)
  Dim iRow As Long, iCol As Long
  iRow = WorksheetFunction.Match(UID, rng.Columns(1), 0)
  iCol = WorksheetFunction.Match(colStr, rng.Rows(1).Offset(-1), 0)
  Get_Table_Property = rng.Cells(iRow, iCol)
End Function

Function Get_Table_Row(sh As String, UID As String) As Long
'Written 04-Apr-2022
'Returns integer of row that starts with UID
  Dim rng As Range
  Set rng = Table_Range(sh)
  Get_Table_Row = WorksheetFunction.Match(UID, rng.Columns(1), 0)
End Function

Function Table_Range(sh As String) As Range
'Written 04-Apr-2022
'Returns range representing table of data with one header row
'Assumes table has one row of header data
  Dim iRow As String, iCol As String
  'Find last used row and column
  iRow = Sheets(sh).Cells(Rows.Count, 1).End(xlUp).row
  iCol = Sheets(sh).Cells(1, 1).End(xlToRight).Column
  'Set range. Exclude header row.
  Set Table_Range = Sheets(sh).Range("A2").Resize(iRow - 1, iCol)
End Function

Sub Remove_Group_Tag(sh As String, UID As String, tag As String)
  
End Sub
