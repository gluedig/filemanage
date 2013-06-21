registerClass = {}

registerClass.registerUser = function(client_mac){
    $.ajax({
     url: "/client/register/"+client_mac,
     type: "GET",
     processData: false,
     contentType: false,
     success: onUserRegisterSuccess,
     error: onUserRegisterError
    });
 };
 
function onUserRegisterSuccess(response, status){
	$(registerClass).trigger('user_register_success', [response, status]);
}

function onUserRegisterError(jqXHR, textStatus, errorMessage) {
   $(registerClass).trigger('user_register_error', [errorMessage]);
}
 
 
registerClass.joinGroup = function(){
	    $.ajax({
	     url: "/group/join",
	     type: "GET",
	     processData: false,
	     contentType: false,
	     dataType: 'text',
	     success: onGroupJoinSuccess,
	     error: onGroupJoinError
	    });
};
 
	 
function onGroupJoinSuccess(response, status){
	$(registerClass).trigger('group_join_success', [response, status]);
}

function onGroupJoinError(jqXHR, textStatus, errorMessage) {
	$(registerClass).trigger('group_join_error', [errorMessage]);
}

registerClass.listMembers = function(){
    $.ajax({
     url: "/group/members",
     type: "GET",
     processData: false,
     contentType: false,
     dataType: 'text',
     success: onGroupMembersSuccess,
     error: onGroupMembersError
    });
};

 
function onGroupMembersSuccess(response, status){
	$(registerClass).trigger('group_members_success', [response, status]);
}

function onGroupMembersError(jqXHR, textStatus, errorMessage) {
	$(registerClass).trigger('group_members_error', [errorMessage]);
}

registerClass.listFiles = function(){
    $.ajax({
     url: "/filebox/list",
     type: "GET",
     processData: false,
     contentType: false,
     dataType: 'text',
     success: onFileListSuccess,
     error: onFileListError
    });
};

 
function onFileListSuccess(response, status){
	$(registerClass).trigger('files_list_success', [response, status]);
}

function onFileListError(jqXHR, textStatus, errorMessage) {
	$(registerClass).trigger('files_list_error', [errorMessage]);
}
