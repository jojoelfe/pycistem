//#include "../core/core_headers.h"
#include "../core/gui_core_headers.h"


#define SERVER_ID 100
#define SOCKET_ID 101

extern MyMovieAssetPanel *movie_asset_panel;
extern MyImageAssetPanel *image_asset_panel;
extern MyParticlePositionAssetPanel *particle_position_asset_panel;
extern MyVolumeAssetPanel *volume_asset_panel;
extern MyRefinementPackageAssetPanel *refinement_package_asset_panel;

extern MyAlignMoviesPanel *align_movies_panel;
extern MyFindCTFPanel *findctf_panel;
extern MyFindParticlesPanel *findparticles_panel;
extern MyRefine3DPanel *refine_3d_panel;

extern MyRunProfilesPanel *run_profiles_panel;
extern MyMovieAlignResultsPanel *movie_results_panel;
extern MyFindCTFResultsPanel *ctf_results_panel;
extern MyPickingResultsPanel *picking_results_panel;
extern MyRefinementResultsPanel *refinement_results_panel;



MyMainFrame::MyMainFrame( wxWindow* parent )
:
MainFrame( parent )
{
//	tree_root = AssetTree->AddRoot("Assets");

	// Add Movies..
	//movie_branch = AssetTree->AppendItem(tree_root, wxString("Movies (0)"));

	socket_server = NULL;
	SetupServer();

	int screen_x_size = wxSystemSettings::GetMetric ( wxSYS_SCREEN_X );
	int screen_y_size = wxSystemSettings::GetMetric ( wxSYS_SCREEN_Y );
	int x_offset;
	int y_offset;

	if (screen_x_size >= 1920 && screen_y_size >= 1080)
	{
		x_offset = (screen_x_size - 1800) / 2;
		y_offset = (screen_y_size - 1180) / 2;

		if (x_offset < 0) x_offset = 0;
		if (y_offset < 0) y_offset = 0;

		SetSize(x_offset, y_offset, 1600, 980);
	}


}

MyMainFrame::~MyMainFrame()
{
	if (socket_server != NULL)
	{
		socket_server->Destroy();
	}
}
void MyMainFrame::SetupServer()
{
	wxIPV4address my_address;
//	wxIPV4address buffer_address;

	for (short int current_port = START_PORT; current_port <= END_PORT; current_port++)
	{

		if (current_port == END_PORT)
		{
			wxPrintf("JOB CONTROL : Could not find a valid port !\n\n");
			Destroy();
			return;
		}

		my_port = current_port;
		my_address.Service(my_port);

		socket_server = new wxSocketServer(my_address);
		socket_server->SetFlags(wxSOCKET_BLOCK | wxSOCKET_WAITALL);

		if ( socket_server->IsOk())
		{
			  // setup events for the socket server..

		   	  socket_server->SetEventHandler(*this, SERVER_ID);
		   	  socket_server->SetNotify(wxSOCKET_CONNECTION_FLAG);
		  	  socket_server->Notify(true);

		  	  this->Connect(SERVER_ID, wxEVT_SOCKET, wxSocketEventHandler( MyMainFrame::OnServerEvent) );

//			  buffer_address.Hostname(wxGetFullHostName()); // hopefully get my ip
			 // my_ip_address = buffer_address.IPAddress();
		      all_my_ip_addresses = ReturnIPAddress();
			  my_port_string = wxString::Format("%hi", my_port);

			  break;
		}
		else
		{
			socket_server->Destroy();
		}
	}

}


void MyMainFrame::RecalculateAssetBrowser(void)
{

/*	wxTreeItemId current_group_branch;

	unsigned long group_counter;
	unsigned long asset_counter;

	long current_group_size;

	bool movies_expanded;

	// need to know the old layout..

	movies_expanded = AssetTree->IsExpanded(movie_branch);


	AssetTree->Freeze();
	AssetTree->DeleteAllItems();

	tree_root = AssetTree->AddRoot("Assets");

	// Add Movies..
	movie_branch = AssetTree->AppendItem(tree_root, wxString("Movies (") + wxString::Format(wxT("%li"), movie_asset_panel->ReturnNumberOfAssets()) + wxString(")"));

		// Movie Groups

		for (group_counter = 0; group_counter < movie_asset_panel->ReturnNumberOfGroups(); group_counter++)
		{
			current_group_size = movie_asset_panel->ReturnGroupSize(group_counter);

			if (current_group_size > 1)
			{
				current_group_branch = AssetTree->AppendItem (movie_branch, movie_asset_panel->ReturnGroupName(group_counter) + wxString(" (")+ wxString::Format(wxT("%li"), current_group_size) + wxString(")"));

				// add the movies..

				for (asset_counter = 0; asset_counter < current_group_size; asset_counter++)
				{
					AssetTree->AppendItem(current_group_branch, movie_asset_panel->ReturnAssetShortFilename(movie_asset_panel->ReturnGroupMember(group_counter, asset_counter)));
				}

			}
		}

	//Images_Branch = main_frame->AssetTree->AppendItem(Tree_Root, "Images (0)");

	// If they were expanded, expand them

	AssetTree->SetItemBold(movie_branch);

	if (movies_expanded == true) AssetTree->Expand(movie_branch);

	AssetTree->Thaw();*/

}


void MyMainFrame::OnCollapseAll( wxCommandEvent& event )
{
	//AssetTree->CollapseAll();
}

void MyMainFrame::OnMenuBookChange( wxBookCtrlEvent& event )
{
	// redo groups..

	align_movies_panel->Refresh();
	movie_results_panel->group_combo_is_dirty = true;

	// We we were editing the particle picking results, and we move away from Results, we may need to do some database stuff
	if ( event.GetOldSelection() == 3)
	{
		picking_results_panel->UpdateResultsFromBitmapPanel();
	}

}

void MyMainFrame::DirtyEverything()
{
	DirtyMovieGroups();
	DirtyImageGroups();
	DirtyRunProfiles();
	DirtyRefinementPackages();
	DirtyInputParameters();
	DirtyParticlePositionGroups();

}

void MyMainFrame::DirtyMovieGroups()
{
	movie_asset_panel->is_dirty = true;
	align_movies_panel->group_combo_is_dirty = true;
	movie_results_panel->group_combo_is_dirty = true;
}

void MyMainFrame::DirtyImageGroups()
{
	image_asset_panel->is_dirty = true;
	findctf_panel->group_combo_is_dirty = true;
	ctf_results_panel->group_combo_is_dirty = true;
	findparticles_panel->group_combo_is_dirty = true;
	picking_results_panel->group_combo_is_dirty = true;
}

void MyMainFrame::DirtyParticlePositionGroups()
{
	particle_position_asset_panel->is_dirty = true;
}

void MyMainFrame::DirtyRefinementPackages()
{
	refinement_package_asset_panel->is_dirty = true;
	refine_3d_panel->refinement_package_combo_is_dirty = true;
	refinement_results_panel->is_dirty=true;
}

void MyMainFrame::DirtyInputParameters()
{
	refine_3d_panel->input_params_combo_is_dirty = true;
}

void MyMainFrame::DirtyRunProfiles()
{
	run_profiles_panel->is_dirty = true;
	align_movies_panel->run_profiles_are_dirty = true;
	findctf_panel->run_profiles_are_dirty = true;
	findparticles_panel->run_profiles_are_dirty = true;
	refine_3d_panel->run_profiles_are_dirty = true;
}


// SOCKETS

void MyMainFrame::OnSocketEvent(wxSocketEvent& event)
{
	MyDebugPrint("MyMainFrame::OnSocketEvent - This should not happen!");
}

void MyMainFrame::OnServerEvent(wxSocketEvent& event)
{
	  SETUP_SOCKET_CODES

	  long current_job;
	  wxString s = _("OnServerEvent: ");
	  wxSocketBase *sock = NULL;

	  switch(event.GetSocketEvent())
	  {
	    case wxSOCKET_CONNECTION : s.Append(_("wxSOCKET_CONNECTION\n")); break;
	    default                  : s.Append(_("Unexpected event !\n")); break;
	  }

	  //MyDebugPrint(s);

      // Accept new connection if there is one in the pending
      // connections queue, else exit. We use Accept(false) for
      // non-blocking accept (although if we got here, there
      // should ALWAYS be a pending connection).

      sock = socket_server->Accept();
	  sock->SetFlags(wxSOCKET_BLOCK | wxSOCKET_WAITALL );//|wxSOCKET_BLOCK);

	  // request identification..
	  //MyDebugPrint(" Requesting identification...");
	  WriteToSocket(sock, socket_please_identify, SOCKET_CODE_SIZE);

	  //MyDebugPrint(" Waiting for reply...");
  	  sock->WaitForRead(5);

      if (sock->IsData() == true)
      {
    	  ReadFromSocket(sock, &socket_input_buffer, SOCKET_CODE_SIZE);

    	  // does this correspond to one of our jobs?

    	  current_job = job_controller.ReturnJobNumberFromJobCode(socket_input_buffer);

  	      if (current_job == -1)
  	      {
  	    	  MyDebugPrint(" GUI : Unknown JOB ID - Closing Connection\n");

  	    	  // incorrect identification - close the connection..
	    	  sock->Destroy();
	    	  sock = NULL;
	      }
	      else
	      {
	    	  MyDebugPrint("Connection from Job #%li", current_job);

	    	  job_controller.job_list[current_job].socket = sock;
	    	  job_controller.job_list[current_job].parent_panel->Bind(wxEVT_SOCKET, &JobPanel::OnJobSocketEvent, job_controller.job_list[current_job].parent_panel, SOCKET_ID);

	    	  sock->SetEventHandler(*job_controller.job_list[current_job].parent_panel, SOCKET_ID);
	    	  //sock->SetEventHandler(*this, SOCKET_ID);
	    	  // Tell the socket it is connected

	    	  WriteToSocket(sock, socket_you_are_connected, SOCKET_CODE_SIZE);

	    	  sock->SetNotify(wxSOCKET_INPUT_FLAG | wxSOCKET_LOST_FLAG);
	    	  sock->Notify(true);
	      }
      }
      else
   	  {
	  	   	   MyDebugPrint(" ...Read Timeout \n\n");
	  	   	   // time out - close the connection
	    	   sock->Destroy();
	    	   sock = NULL;
	  }
}

void MyMainFrame::OnFileNewProject( wxCommandEvent& event )
{
	MyNewProjectWizard *my_wizard = new MyNewProjectWizard(this);
	my_wizard->GetPageAreaSizer()->Add(my_wizard->m_pages.Item(0));
	my_wizard->RunWizard(my_wizard->m_pages.Item(0));

	if (current_project.is_open == true)
	{
		SetTitle("cisTEM - [" + current_project.project_name + "]");
	}

}

void MyMainFrame::OnFileOpenProject( wxCommandEvent& event )
{
	// find a DB file..

	if (current_project.is_open)
	{
	    if (wxMessageBox("The current project must be closed before opening a new project.\n\nClose it now?", "Please confirm", wxICON_QUESTION | wxYES_NO, this) == wxNO ) return;

	    current_project.Close();
		SetTitle("cisTEM");

	}

	wxFileDialog openFileDialog(this, _("Open db file"), "", "", "DB files (*.db)|*.db", wxFD_OPEN|wxFD_FILE_MUST_EXIST);

	if (openFileDialog.ShowModal() == wxID_CANCEL) return;     // the user changed idea...

	if (current_project.OpenProjectFromFile(openFileDialog.GetPath()) == true)
	{
		OneSecondProgressDialog *my_dialog = new OneSecondProgressDialog ("Open Project", "Opening Project", 9, this);
		SetTitle("cisTEM - [" + current_project.project_name + "]");

		movie_asset_panel->ImportAllFromDatabase();
		my_dialog->Update(1, "Opening project (loading image assets...)");
		image_asset_panel->ImportAllFromDatabase();
		my_dialog->Update(2, "Opening project (loading particle position assets...)");
		particle_position_asset_panel->ImportAllFromDatabase();
		my_dialog->Update(3, "Opening project (loading run profiles...)");
		run_profiles_panel->ImportAllFromDatabase();
		my_dialog->Update(4, "Opening project (loading volume assets...)");
		volume_asset_panel->ImportAllFromDatabase();
		my_dialog->Update(5, "Opening project (loading Refinement Packages...)");
		refinement_package_asset_panel->ImportAllFromDatabase();
		//align_movies_panel->Refresh();
		my_dialog->Update(6, "Opening project (loading movie alignment results...)");
		movie_results_panel->FillBasedOnSelectCommand("SELECT DISTINCT MOVIE_ASSET_ID FROM MOVIE_ALIGNMENT_LIST");
		my_dialog->Update(7, "Opening project (loading CTF estimation results...)");
		ctf_results_panel->FillBasedOnSelectCommand("SELECT DISTINCT IMAGE_ASSET_ID FROM ESTIMATED_CTF_PARAMETERS");
		my_dialog->Update(8, "Opening project (finishing...)");
		picking_results_panel->OnProjectOpen();
		my_dialog->Update(9, "Opening project (all done)");

		DirtyEverything();

		my_dialog->Destroy();
	}
	else
	{
		MyPrintWithDetails("An error occured opening the database file..");
	}



}

void MyMainFrame::OnFileExit( wxCommandEvent& event )
{
	Close(true);

}

void MyMainFrame::OnFileCloseProject( wxCommandEvent& event )
{
	current_project.Close();

	movie_asset_panel->Reset();
	image_asset_panel->Reset();
	volume_asset_panel->Reset();
	particle_position_asset_panel->Reset();
	refinement_package_asset_panel->Reset();
	RecalculateAssetBrowser();
	run_profiles_panel->Reset();
	movie_results_panel->Clear();
	ctf_results_panel->Clear();
	picking_results_panel->OnProjectClose();


	SetTitle("cisTEM");

}
void MyMainFrame::OnFileMenuUpdate( wxUpdateUIEvent& event )
{
	if (current_project.is_open == true)
	{
		FileMenu->FindItem(FileMenu->FindItem("Close Project"))->Enable(true);
		ExportMenu->FindItem(ExportMenu->FindItem("Export coordinates to Imagic"))->Enable(true);
		ExportMenu->FindItem(ExportMenu->FindItem("Export to Frealign"))->Enable(true);
	}
	else
	{
		FileMenu->FindItem(FileMenu->FindItem("Close Project"))->Enable(false);
		ExportMenu->FindItem(ExportMenu->FindItem("Export coordinates to Imagic"))->Enable(false);
		ExportMenu->FindItem(ExportMenu->FindItem("Export to Frealign"))->Enable(false);
	}
}

void MyMainFrame::OnExportCoordinatesToImagic ( wxCommandEvent & event )
{
	MyParticlePositionExportDialog *export_dialog = new MyParticlePositionExportDialog(this);
	export_dialog->ShowModal();
}

void MyMainFrame::OnExportToFrealign ( wxCommandEvent & event )
{
	MyFrealignExportDialog *export_dialog = new MyFrealignExportDialog(this);
	export_dialog->ShowModal();
}
