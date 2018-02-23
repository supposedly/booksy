import { Component } from '@angular/core';

@Component({ // this is the searchbar
  selector: 'app-mgmt-media',
  template: `<media-search-bar with-delete default="all"></media-search-bar>`,
  styles: [],
})
export class MgmtMediaComponent {}

@Component({})
export class MgmtMediaHeaderComponent {

}
