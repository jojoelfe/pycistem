#ifndef __ErrorDialog__
#define __ErrorDialog__

/**
@file
Subclass of ErrorDialog, which is generated by wxFormBuilder.
*/

#include "ProjectX_gui.h"

//// end generated include

/** Implementing ErrorDialog */
class MyErrorDialog : public ErrorDialog
{
	public:
		/** Constructor */
		MyErrorDialog( wxWindow* parent );
	//// end generated class members

		void OnClickOK( wxCommandEvent& event );
	
};

#endif // __ErrorDialog__
