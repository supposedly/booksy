// This file formerly had some logic
// but it was pretty-much-entirely redundant to the media-search stuff
// so I made the search bar into a modular component and replaced this with that
// (component being media-search-bar)

import { Component } from '@angular/core';

@Component({
  selector: 'app-mgmt-media',
  template: '<media-search-bar with-delete default="all"></media-search-bar>',
  styles: [],
})
export class MgmtMediaComponent {}
