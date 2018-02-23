import { Component, OnChanges, Input } from '@angular/core';

import { MgmtHeaderButtonService } from '../mgmt-header-button.service';

import { NavButton } from '../classes';

@Component({
  selector: 'app-mgmt-header',
  template: '<generic-header [buttons]="buttons"></generic-header>',
  styles: ['']
})
export class MgmtHeaderComponent implements OnChanges {
  buttons: NavButton[] = null;
  
  constructor(
    private buttonService: MgmtHeaderButtonService,
  ) {}
  
  @Input() uID: string;

  ngOnChanges() {
    this.getButtons();
  }

  getButtons(): void {
    if (!this.buttons) {
      this.buttonService.getButtons(this.uID)
        .subscribe(buttons => this.buttons = buttons);
    }
  }

}
