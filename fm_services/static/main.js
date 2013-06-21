function handleJoinSuccess(response, status){
	 console.log("Group join OK: "+status);
	 $('#group_name').empty().append(status);
	 setTimeout(function(){registerClass.listMembers()}, 100);
	 setTimeout(function(){registerClass.listFiles()}, 200);
	 setTimeout(function(){start_polling()}, 1000);
}

$(registerClass).on('group_join_success', handleJoinSuccess);
 
function handleRegisterSuccess(response, status){
	console.log("Registration OK: "+status);
	registerClass.joinGroup();
}
 
$(registerClass).on('user_register_success', handleRegisterSuccess);

function handleMembersSuccess(response, status){
	
	console.log("Group members: ");
	members = status.split('\n')
	if (members.length > 0) {
		$('#members_table').empty();
	}
	members.forEach(function(member) {
		  console.log(member);
		  $('#members_table').append('<tr id="member_'+member+'"><td>'+member+'</td></tr>');
	});	
}
 
$(registerClass).on('group_members_success', handleMembersSuccess);

function handleFilesListSuccess(response, status){
	
	console.log("Group files: ");
	files = status.split('\n')
	if (files.length > 0 && files[0] != '') {
		$('#files_table').empty();
	}
	files.forEach(function(file) {
		  console.log(file);
		  $('#files_table').append('<tr id="file_'+file+'"><td><a target="_blank" href="/filebox/download/'+file+'">'+file+'</td></tr>');
	});	
}
 
$(registerClass).on('files_list_success', handleFilesListSuccess);

function start_polling()
{
	var source_group = new EventSource('/updates/group');
    source_group.onmessage = function(e){sse_message_group(e)};
	source_group.onerror = function(s){alert(s)};

	var source_group = new EventSource('/updates/files');
    source_group.onmessage = function(e){sse_message_file(e)};
	source_group.onerror = function(s){alert(s)};	
};

function sse_message_group(e) {
	var data = jQuery.parseJSON(e.data);
	var item = 'msgtype: '+data.msgtype+' group_id: '+data.group_id+' mac: '+data.client;
	console.log(item);
/*
	$('#members_table tr').each(function(index){
		console.log($(this).attr('id'));
	});
*/	
	if (data.msgtype == 'add-member') {
		console.log('adding group member: '+data.client);
		var found = false;
		$('#members_table tr').each(function(index){
			var id = $(this).attr('id');
			if (id == 'member_'+data.client) {
				found = true;
			}
		});
		if (!found){
			$('#members_table').append('<tr id="member_'+data.client+'"><td>'+data.client+'</td></tr>');
		}
		
	} else if (data.msgtype == 'remove-member') {
		console.log('removing group member: '+data.client);
		$('#members_table tr[id=member_'+data.client+']').remove();
	}

}; 	

function sse_message_file(e) {
	var data = jQuery.parseJSON(e.data);
	var item = 'msgtype: '+data.msgtype+' group_id: '+data.group_id+' mac: '+data.client+' filename: '+data.filename;
	console.log(item);
	
	if (data.msgtype == 'file-upload') {
		console.log('adding file: '+data.filename);
		var found = false;
		$('#files_table tr').each(function(index){
			var id = $(this).attr('id');
			if (id == 'file_'+data.filename) {
				found = true;
			}
		});
		if (!found){
			$('#files_table').append('<tr id="file_'+data.filename+'"><td><a target="_blank" href="/filebox/download/'+data.filename+'">'+data.filename+'</td></tr>');
		}
		
	}
};


