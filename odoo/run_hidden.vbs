' Lance un .bat SANS ouvrir de fenetre de console.
'
' Les taches planifiees Teatower tournent en session interactive : cmd.exe
' affiche donc une fenetre a chaque execution (toutes les 15 min pour
' "Teatower - Retrait pret Shopify"). Passer la tache en S4U ("executer meme
' si l'utilisateur n'est pas connecte") demande des droits admin ; ce lanceur
' fait la meme chose sans admin.
'
' Usage dans la tache planifiee :
'   Programme  : C:\Windows\System32\wscript.exe
'   Arguments  : "C:\...\odoo\run_hidden.vbs" "C:\...\odoo\shopify_retrait_pret.bat"
'
' Le .bat continue d'ecrire son log normalement ; seule la fenetre disparait.

If WScript.Arguments.Count = 0 Then
  WScript.Quit 2
End If

Dim sh, cmd, i
Set sh = CreateObject("WScript.Shell")

cmd = """" & WScript.Arguments(0) & """"
For i = 1 To WScript.Arguments.Count - 1
  cmd = cmd & " """ & WScript.Arguments(i) & """"
Next

' 0 = fenetre masquee, False = ne pas attendre la fin
sh.Run cmd, 0, False
