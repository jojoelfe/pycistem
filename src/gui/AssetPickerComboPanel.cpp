#include "../core/gui_core_headers.h"

extern MyVolumeAssetPanel *volume_asset_panel;
extern MyRefinementPackageAssetPanel *refinement_package_asset_panel;

AssetPickerComboPanel::AssetPickerComboPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style)
: AssetPickerComboPanelParent(parent, id, pos, size, style)
{
	wxLogNull *suppress_png_warnings = new wxLogNull;
	#include "icons/window_plus_icon_16.cpp"
	wxBitmap window_plus_icon = wxBITMAP_PNG_FROM_DATA(window_plus_icon_16);
	WindowSelectButton->SetBitmap(window_plus_icon);

	Bind(wxEVT_BUTTON, &AssetPickerComboPanel::ParentPopUpSelectorClicked, this);

}

void AssetPickerComboPanel::ParentPopUpSelectorClicked(wxCommandEvent& event)
{
	if (AssetComboBox->GetCount() > 0) GetAssetFromPopup();
}


void AssetPickerComboPanel::GetAssetFromPopup()
{
	int counter;
	ListCtrlDialog *picker_dialog = new ListCtrlDialog(this, wxID_ANY, "Make a selection :-");

	picker_dialog->MyListCtrl->InsertColumn(0, "Column1", wxLIST_FORMAT_LEFT, wxLIST_AUTOSIZE);

	if (AssetComboBox->GetCount() > 0 )
	{

		for (counter = 0; counter < AssetComboBox->GetCount(); counter++)
		{
			picker_dialog->MyListCtrl->InsertItem(counter, AssetComboBox->GetString(counter), counter);
		}

		if (AssetComboBox->GetSelection() == -1)
		{
			picker_dialog->MyListCtrl->SetItemState(0, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED);
			picker_dialog->MyListCtrl->EnsureVisible(0);
		}
		else
		{
			picker_dialog->MyListCtrl->SetItemState(AssetComboBox->GetSelection(), wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED);
			picker_dialog->MyListCtrl->EnsureVisible(AssetComboBox->GetSelection());
		}

		int client_width;
		int client_height;
		int current_width;

		picker_dialog->MyListCtrl->GetClientSize(&client_width, &client_height);
		picker_dialog->MyListCtrl->SetColumnWidth(0, wxLIST_AUTOSIZE);

		current_width = picker_dialog->MyListCtrl->GetColumnWidth(0);

		if (client_width > current_width) picker_dialog->MyListCtrl->SetColumnWidth(0, client_width);
	}

	if (picker_dialog->ShowModal() == wxID_OK)
	{
		int selected_item = picker_dialog->MyListCtrl->GetNextItem(-1, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED);

		if (selected_item != -1)
		{
			SetSelectionWithEvent(selected_item);
		}
	}

	picker_dialog->Destroy();

}


VolumeAssetPickerComboPanel::VolumeAssetPickerComboPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style)
: AssetPickerComboPanel(parent, id, pos, size, style)
{

}

RefinementPackagePickerComboPanel::RefinementPackagePickerComboPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style)
: AssetPickerComboPanel(parent, id, pos, size, style)
{

}

RefinementPickerComboPanel::RefinementPickerComboPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style)
: AssetPickerComboPanel(parent, id, pos, size, style)
{

}

ClassificationPickerComboPanel::ClassificationPickerComboPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style)
: AssetPickerComboPanel(parent, id, pos, size, style)
{

}

ImageGroupPickerComboPanel::ImageGroupPickerComboPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style)
: AssetPickerComboPanel(parent, id, pos, size, style)
{

}

MovieGroupPickerComboPanel::MovieGroupPickerComboPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style)
: AssetPickerComboPanel(parent, id, pos, size, style)
{

}

ImagesPickerComboPanel::ImagesPickerComboPanel(wxWindow* parent, wxWindowID id, const wxPoint& pos, const wxSize& size, long style)
: AssetPickerComboPanel(parent, id, pos, size, style)
{

}





/*
void VolumeAssetPickerComboPanel::GetAssetFromPopup()
{
	int counter;
	ListCtrlDialog *picker_dialog = new ListCtrlDialog(this, wxID_ANY, "Select a Volume Asset");

	picker_dialog->MyListCtrl->InsertColumn(0, "Volume Asset", wxLIST_FORMAT_LEFT, wxLIST_AUTOSIZE);

	for (counter = 0; counter < volume_asset_panel->all_assets_list->number_of_assets; counter++)
	{
		picker_dialog->MyListCtrl->InsertItem(counter, volume_asset_panel->ReturnAssetName(counter), counter);
	}

	if (volume_asset_panel->all_assets_list->number_of_assets > 0)
	{
		if (AssetComboBox->GetSelection() == -1)
		{
			picker_dialog->MyListCtrl->SetItemState(0, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED);
			picker_dialog->MyListCtrl->EnsureVisible(0);
		}
		else
		{
			picker_dialog->MyListCtrl->SetItemState(AssetComboBox->GetSelection(), wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED);
			picker_dialog->MyListCtrl->EnsureVisible(AssetComboBox->GetSelection());
		}
	}

	int client_width;
	int client_height;
	int current_width;

	picker_dialog->MyListCtrl->GetClientSize(&client_width, &client_height);
	picker_dialog->MyListCtrl->SetColumnWidth(0, wxLIST_AUTOSIZE);

	current_width = picker_dialog->MyListCtrl->GetColumnWidth(0);

	if (client_width > current_width) picker_dialog->MyListCtrl->SetColumnWidth(0, client_width);

	if (picker_dialog->ShowModal() == wxID_OK)
	{
		int selected_item = picker_dialog->MyListCtrl->GetNextItem(-1, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED);

		if (selected_item != -1)
		{
			SetSelectionWithEvent(selected_item);

		}
	}

	picker_dialog->Destroy();
}

bool VolumeAssetPickerComboPanel::FillComboBox()
{
	return AssetComboBox->FillWithVolumeAssets();
}


void RefinementPackagePickerComboPanel::GetAssetFromPopup()
{
	int counter;
	ListCtrlDialog *picker_dialog = new ListCtrlDialog(this, wxID_ANY, "Select a Refinement Package Asset");

	picker_dialog->MyListCtrl->InsertColumn(0, "Refinement Package Asset", wxLIST_FORMAT_LEFT, wxLIST_AUTOSIZE);

	for (counter = 0; counter < refinement_package_asset_panel->all_refinement_packages.GetCount(); counter++)
	{
		picker_dialog->MyListCtrl->InsertItem(counter, refinement_package_asset_panel->all_refinement_packages[counter].name, counter);
	}

	if (refinement_package_asset_panel->all_refinement_packages.GetCount() > 0)
	{
		if (AssetComboBox->GetSelection() == -1)
		{
			picker_dialog->MyListCtrl->SetItemState(0, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED);
			picker_dialog->MyListCtrl->EnsureVisible(0);
		}
		else
		{
			picker_dialog->MyListCtrl->SetItemState(AssetComboBox->GetSelection(), wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED);
			picker_dialog->MyListCtrl->EnsureVisible(AssetComboBox->GetSelection());
		}
	}

	int client_width;
	int client_height;
	int current_width;

	picker_dialog->MyListCtrl->GetClientSize(&client_width, &client_height);
	picker_dialog->MyListCtrl->SetColumnWidth(0, wxLIST_AUTOSIZE);

	current_width = picker_dialog->MyListCtrl->GetColumnWidth(0);

	if (client_width > current_width) picker_dialog->MyListCtrl->SetColumnWidth(0, client_width);

	if (picker_dialog->ShowModal() == wxID_OK)
	{
		int selected_item = picker_dialog->MyListCtrl->GetNextItem(-1, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED);

		if (selected_item != -1)
		{
			SetSelectionWithEvent(selected_item);
		}
	}

	picker_dialog->Destroy();
}

bool  RefinementPackagePickerComboPanel::FillComboBox()
{
	return AssetComboBox->FillWithRefinementPackages();
}



void RefinementPickerComboPanel::GetAssetFromPopup()
{
	int counter;
	ListCtrlDialog *picker_dialog = new ListCtrlDialog(this, wxID_ANY, "Select Refinement Parameters");

	picker_dialog->MyListCtrl->InsertColumn(0, "Refinement", wxLIST_FORMAT_LEFT, wxLIST_AUTOSIZE);

	if (current_refinement_package >0 )
	{

		for (counter = 0; counter < refinement_package_asset_panel->all_refinement_packages[current_refinement_package].refinement_ids.GetCount(); counter++)
		{
			picker_dialog->MyListCtrl->InsertItem(counter, refinement_package_asset_panel->ReturnPointerToShortRefinementInfoByRefinementID(refinement_package_asset_panel->all_refinement_packages[current_refinement_package].refinement_ids[counter])->name, counter);
		}

		if (refinement_package_asset_panel->all_refinement_packages.GetCount() > 0)
		{
			if (AssetComboBox->GetSelection() == -1)
			{
				picker_dialog->MyListCtrl->SetItemState(0, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED);
				picker_dialog->MyListCtrl->EnsureVisible(0);
			}
			else
			{
				picker_dialog->MyListCtrl->SetItemState(AssetComboBox->GetSelection(), wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED);
				picker_dialog->MyListCtrl->EnsureVisible(AssetComboBox->GetSelection());
			}
		}

		int client_width;
		int client_height;
		int current_width;

		picker_dialog->MyListCtrl->GetClientSize(&client_width, &client_height);
		picker_dialog->MyListCtrl->SetColumnWidth(0, wxLIST_AUTOSIZE);

		current_width = picker_dialog->MyListCtrl->GetColumnWidth(0);

		if (client_width > current_width) picker_dialog->MyListCtrl->SetColumnWidth(0, client_width);
	}

	if (picker_dialog->ShowModal() == wxID_OK)
	{
		int selected_item = picker_dialog->MyListCtcurrent_refinement_package = -1;rl->GetNextItem(-1, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED);

		if (selected_item != -1)
		{
			SetSelectionWithEvent(selected_item);
		}
	}

	picker_dialog->Destroy();
}

bool  RefinementPickerComboPanel::FillComboBox(long wanted_refinement_package)
{
	return AssetComboBox->FillWithRefinements(wanted_refinement_package);
	current_refinement_package = wanted_refinement_package;
}
*/

