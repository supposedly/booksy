import { Component, OnInit, Input } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';

import { SideButton } from '../classes';
import { SideButtonService } from '../side-button.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent /*implements OnInit*/ {
  buttons: SideButton[] = null;
  public san;
  
  constructor(
    private sideButtonService: SideButtonService,
    private sanitizer: DomSanitizer
  ) {
      this.san = sanitizer.bypassSecurityTrustStyle;
  }
  
  @Input() uID: string;
  
  ngOnChanges() {
    this.getButtons();
  }
  
  /*
  ngOnInit() {
    this.getButtons();
  }
  */
  
  getButtons(): void {
    if (!this.buttons) {
      this.sideButtonService.getButtons(this.uID)
        .subscribe(buttons => this.buttons = buttons);
    }
  }

}
