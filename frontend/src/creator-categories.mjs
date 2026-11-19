export function categoryChoices(categories=[]){
 const byId=new Map(categories.map(c=>[Number(c.id),c]));
 return categories.map(category=>{const names=[category.name],seen=new Set([Number(category.id)]);let parent=Number(category.parentId);while(parent&&byId.has(parent)&&!seen.has(parent)){seen.add(parent);const row=byId.get(parent);names.unshift(row.name);parent=Number(row.parentId);}return {...category,label:names.join(' / ')};});
}
