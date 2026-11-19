// Frontend compatibility only. Never intercept backend API or OAuth callback requests.
const aliases=new Map([
 ['/user','account'],['/login','account'],['/userLogin','account'],['/view/user.php','account'],['/view/userLogin.php','account'],
 ['/signUp','signup'],['/view/signUp.php','signup'],['/recoverPass','recover'],['/view/recoverPass.php','recover'],
 ['/mvideos','videos'],['/view/managerVideos.php','videos'],['/upload','upload'],['/view/mini-upload-form','upload'],
 ['/Encoder','queue'],['/Encoder/index.php','queue'],['/plugin/BulkEmbed/search.php','embed'],['/liveStudio','studio']
]);
export function legacyCreatorView(path,search=''){
 const view=aliases.get(path.replace(/\/$/,''));if(!view)return null;const query=new URLSearchParams(search);
 return {view:view==='videos'&&query.get('link')==='1'?'embed':view};
}
