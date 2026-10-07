import xmlrpc.client, os
U='https://tea-tree.odoo.com'; D='tsc-be-tea-tree-main-18515272'
P=os.environ.get('ODOO_PWD')
if not P:
    import winreg
    k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Environment'); P=winreg.QueryValueEx(k,'ODOO_PWD')[0]
uid=xmlrpc.client.ServerProxy(U+'/xmlrpc/2/common').authenticate(D,'nicolas.raes@teatower.com',P,{})
m=xmlrpc.client.ServerProxy(U+'/xmlrpc/2/object',allow_none=True)
def x(model,meth,*a,**k): return m.execute_kw(D,uid,P,model,meth,list(a),k)
L=[  # (pid, qty, libellé BL)
(7709,329*12,'329 ctn Lait éclaircissant EXTRA FORT vanille 500 ml'),
(7889,619*12,'619 ctn Lait éclaircissant TRÈS FORT vanille 500 ml'),
(7888,407*12,'407 ctn Lait éclaircissant ULTRA FORT vanille 500 ml'),
(7884,7278,'607 ctn Lait éclaircissant huile de carotte 500 ml (7.284 u au BL, 7.278 en stock)'),
(7886,516,'50 ctn Gel douche gommant vanille 500 ml (600 u au BL, 516 en stock)'),
(7887,515,'50 ctn Gel douche gommant amande 500 ml (600 u au BL, 515 en stock)'),
(7899,756*48,'756 ctn x48 Savon gommant éclaircissant 2 en 1 200 g (882 au BDC)'),
(7873,6720,'192 ctn Disques cosmétiques coton 120x (sachets)'),
]+[(p,2,'Kit échantillonnage Oxyprolane x2') for p in (7867,7868,7869,7870,7871)]
so=x('sale.order','create',{'partner_id':123541,'partner_invoice_id':123541,'partner_shipping_id':123541,'pricelist_id':1,'fiscal_position_id':1,'warehouse_id':1,'team_id':1,'user_id':6,
 'client_order_ref':'Sortie container BL MEDURR024346 / F26-09-46 (Globex Trading, Kribi)',
 'order_line':[(0,0,{'product_id':p,'product_uom_qty':q,'price_unit':0.0,'tax_id':[(6,0,[3])]}) for p,q,_ in L]})
for i,(l,(p,q,t)) in enumerate(zip(x('sale.order.line','search_read',[['order_id','=',so]],fields=['id'],order='sequence,id'),L)):
    x('sale.order.line','write',[l['id']],{'name':x('sale.order.line','read',[l['id']],fields=['name'])[0]['name']+'\n'+t})
try: x('sale.order','action_confirm',[so])
except Exception as e: print('confirm:',str(e)[:200])
print(x('sale.order','read',[so],fields=['name','state','picking_ids']))
